import datetime
import typing

from covid_data_miner.src.domain import CovidPoint
from covid_data_miner.src.projections.base_projection import BaseProjection


class HistoricalDataSummaryProjection(BaseProjection):
    description = "Aggregate spare CovidPoints into <time_interval> summaries using <last> group by <tag>"

    def __init__(
        self,
        origin_measurement,
        interval=14400,  # 4 Hours
        key='country',
        projection_name=None
    ):
        super().__init__()
        self.origin_measurement = origin_measurement
        self.interval = interval
        self.TEMPLATE = dict(
            confirmed_cumulative=0,
            hospitalized_cumulative=0,
            severe_cumulative=0,
            death_cumulative=0,
            recovered_cumulative=0,
            confirmed_diff=0,
            hospitalized_diff=0,
            severe_diff=0,
            death_diff=0,
            recovered_diff=0,
            time=0,
            country="",
            city="",
            region=""
        )
        self.key = key
        self._projection_name = projection_name
        assert projection_name

    @property
    def name(self):
        return self._projection_name

    def _get_previous_and_current_values(self, value, timestamp, relevants):
        try:
            previous = relevants[f'{timestamp - self.interval}|{value}']
            assert previous[self.key] == value, (previous[self.key], value, self.key)
        except KeyError:
            point = self.repository.get_points_from_projections(self._projection_name, self.key, (value, timestamp))
            point = point and point[0]
            if point:
                previous = self._point_to_projection(point)
            else:
                previous = {k: v for k, v in self.TEMPLATE.items()}
                previous[self.key] = value
                previous['time'] = timestamp - self.interval
        try:
            current = relevants[f'{timestamp}|{value}']
            assert current[self.key] == value, (current[self.key], value, self.key)
        except KeyError:
            point = self.repository.get_points_from_projections(self._projection_name, self.key, (value, timestamp))
            point = point and point[0]
            if point:
                current = self._point_to_projection(point)
            else:
                current = {k: v for k, v in self.TEMPLATE.items()}
                current[self.key] = value
                current['time'] = timestamp
        return {'previous': previous, 'current': current}

    def _get_relevant_projections_for_points(self, points: typing.List[CovidPoint]):
        _timestamps = []
        _Ts = []
        for point in points:
            _p = [
                point.last_update - (point.last_update % self.interval) - self.interval,
                point.last_update - (point.last_update % self.interval),
                point.last_update - (point.last_update % self.interval) + self.interval
            ]
            for p in _p:
                if (p, getattr(point, self.key)) not in _timestamps:
                    _timestamps.append((p, getattr(point, self.key)))
        params = [(t[1], t[0] - self.interval) for t in _timestamps]
        projection_points = self.repository.get_points_from_projections(self._projection_name, self.key, *params)
        res = {}
        for point in projection_points:
            try:
                res[f'{point["time"]}|{point[self.key]}'] = self._point_to_projection(point)
            except:
                print('Error with point: %s' % point)
                raise
        return res

    def _make_projection(self, point, relevants):
        key = self._normalize_key(self.key, getattr(point, self.key))
        current_timestamp = point.last_update - (point.last_update % self.interval) + self.interval
        data = self._get_previous_and_current_values(key, current_timestamp, relevants)
        current, previous = data["current"], data["previous"]

        for k in [x for x in ["country", "region", "city"] if x != self.key]:
            current[k] = self._normalize_key(k, getattr(point, k))
        current.update(
            {
                "time": current_timestamp,
                "confirmed_cumulative": point.confirmed_cumulative,
                "hospitalized_cumulative": point.hospitalized_cumulative,
                "severe_cumulative": point.severe_cumulative,
                "death_cumulative": point.death_cumulative,
                "recovered_cumulative": point.recovered_cumulative
            }
        )
        current.update(
            {
                "confirmed_diff": current['confirmed_cumulative'] - previous['confirmed_cumulative'],
                "hospitalized_diff": current['hospitalized_cumulative'] - previous['hospitalized_cumulative'],
                "severe_diff": current['severe_cumulative'] - previous['severe_cumulative'],
                "death_diff": current['death_cumulative'] - previous['death_cumulative'],
                "recovered_diff": current['recovered_cumulative'] - previous['recovered_cumulative'],
            }
        )
        relevants[f'{current_timestamp}|{current[self.key]}'] = current
        return current
                
    def project(self, points: typing.List[CovidPoint], disable_plugins=False):
        relevants = self._get_relevant_projections_for_points(points)
        projections = []
        for point in points:
            projection = self._make_projection(point, relevants)
            projection and projections.append(projection)
        projections and self.repository.save_projections(self._projection_name, *projections)
        if not disable_plugins:
            for observer in self.observers:
                for projection in projections:
                    observer.on_projection(projection)
        return projections

    def rewind(self, since: datetime.datetime = None, disable_plugins: bool = False) -> typing.Dict:
        first_point_time = int(since.strftime('%s')) if since else \
            self.repository.get_first_update_for_source(self.origin_measurement)
        last_point_time = self.repository.get_last_update_for_source(self.origin_measurement)
        if not first_point_time or first_point_time < 0:
            return {
                "rewind": False,
                "first_point": first_point_time,
                "last_point": last_point_time
            }
        print('Rewind from first_point %s to last_point %s' % (first_point_time, last_point_time))
        next_point = first_point_time - (first_point_time % self.interval) + self.interval
        last_point = last_point_time - (last_point_time % self.interval) + self.interval
        self.repository.delete_points_for_projection(self._projection_name, next_point, last_point)
        for timestamp in range(next_point, last_point + self.interval, self.interval):
            data = self.repository.get_nearest_historical_points_by_fields(
                timestamp, self.origin_measurement, self.key
            )
            self.project(data, disable_plugins=disable_plugins)
        return {
            "rewind": True,
            "first_point": next_point,
            "last_point": last_point
        }

    def _point_to_projection(self, point):
        return {
            "time": point['time'],
            "country": point['country'] or '',
            "region": point['region'] or '',
            "city": point['city'] or '',
            "confirmed_cumulative": point['confirmed_cumulative'],
            "hospitalized_cumulative": point['hospitalized_cumulative'],
            "severe_cumulative": point['severe_cumulative'],
            "death_cumulative": point['death_cumulative'],
            "recovered_cumulative": point['recovered_cumulative'],
            "confirmed_diff": point['confirmed_diff'],
            "hospitalized_diff": point['hospitalized_diff'],
            "severe_diff": point['severe_diff'],
            "death_diff": point['death_diff'],
            "recovered_diff": point['recovered_diff']
        }
