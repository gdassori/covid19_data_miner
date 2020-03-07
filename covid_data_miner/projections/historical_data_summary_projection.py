import datetime
import time
import typing

from covid_data_miner.domain import CovidPoint
from covid_data_miner.projections.base_projection import BaseProjection


class HistoricalDataSummaryProjection(BaseProjection):
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
            updated_at=0,
            country="",
            city="",
            region=""
        )
        self.key = key
        self._projection_name = projection_name or f'summary_{self.origin_measurement}_{self.key}'

    def _get_previous_and_current_values(self, value, timestamp, relevants):
        try:
            previous = relevants[timestamp - self.interval]
            assert previous[self.key] == value
        except KeyError:
            previous = {k: v for k, v in self.TEMPLATE.items()}
            previous[f'tag:{self.key}'] = value
            previous['time'] = timestamp - self.interval
        try:
            current = relevants[timestamp]
            assert current[self.key] == value
        except KeyError:
            current = {k: v for k, v in self.TEMPLATE.items()}
            current[f'tag:{self.key}'] = value
            previous['time'] = timestamp
        return {'previous': previous, 'current': current}

    def _get_relevant_projections_for_points(self, points: typing.List[CovidPoint]):
        _timestamps = [(point.last_update % self.interval + self.interval) for point in points]
        previous_timestamps = [t - self.interval for t in _timestamps]
        timestamps = sorted(set(_timestamps) | set(previous_timestamps))
        return self.repository.get_projections_with_timestamps(self._projection_name, *timestamps)

    def _make_projection(self, point, relevants):
        key = self._normalize_key(self.key, getattr(point, self.key))
        current_timestamp = point.last_update - (point.last_update % self.interval) + self.interval
        data = self._get_previous_and_current_values(key, current_timestamp, relevants)
        current, previous = data["current"], data["previous"]
        if current["updated_at"] > point.last_update:
            return
        assert current[self.key] == key
        for k in [x for x in ["country", "region", "city"] if x != self.key]:
            current[k] = self._normalize_key(k, getattr(point, k))
        current.update(
            {
                "time": current_timestamp,
                "updated_at": point.last_update,
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
        relevants["current"][current_timestamp] = current
        return current
                
    def project(self, points: typing.List[CovidPoint]):
        relevants = self._get_relevant_projections_for_points(points)
        projections = []
        for point in points:
            projections.append(self._make_projection(point, relevants))
        self.repository.save_projections(self._projection_name, *projections)
        for observer in self.observers:
            for projection in projections:
                observer.on_projection(projection)
        return projections

    def rewind(self, since: datetime.datetime = None, to: datetime.datetime = None) -> typing.Dict:
        to = to or int(time.time())
        first_point_time = int(since.strftime('%s')) if since else \
            self.repository.get_first_historical_point_time_for_measurement(self.origin_measurement)
        last_point_time = int(to.strftime('%s')) if to else int(time.time())
        if not first_point_time or first_point_time < 0:
            return {}
        next_point = first_point_time % self.interval + self.interval
        last_point = last_point_time % self.interval
        report = {}
        for timestamp in range(next_point, last_point + self.interval, self.interval):
            data = self.repository.get_nearest_historical_points_by_fields(
                timestamp, self.origin_measurement, self.key
            )
            self.project(data)
        return report
