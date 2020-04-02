import abc
import threading
import typing

import influxdb as influxdb
from influxdb import InfluxDBClient

from covid_data_miner.src.domain import CovidPoint, IstatDeathRatePoint
from covid_data_miner.src.utils import chunks


class InfluxDBRepository(metaclass=abc.ABCMeta):
    def __init__(self, influxdb_client: influxdb.InfluxDBClient):
        self._influxdb_client = influxdb_client
        self._db_created = False
        self._lock = threading.RLock()
        self.databases = []

    @property
    def influxdb_client(self) -> influxdb.InfluxDBClient:
        if self._db_created:
            return self._influxdb_client
        with self._lock:
            if not self._db_created:
                for db in self.databases:
                    self._influxdb_client.create_database(db)
            self._db_created = True
        return self._influxdb_client


class InfluxDataRepository(InfluxDBRepository):
    def __init__(self, influxdb_client: InfluxDBClient):
        super().__init__(influxdb_client)
        self.databases = ['covid19']
        self.influxdb_client.ping()

    def save_historical_points(self, *points: (CovidPoint, IstatDeathRatePoint)):
        if not points:
            return
        if isinstance(points[0], CovidPoint):
            return self._save_covid_points(points)
        elif isinstance(points[0], IstatDeathRatePoint):
            return self._save_istat_points(points)
        else:
            raise ValueError('Error, unknown format')

    def _save_istat_points(self, points: IstatDeathRatePoint):
        for chunk in chunks(points, 10000):
            saving_points = [
                {
                    "measurement": point.source,
                    "time": int(point.timestamp.strftime('%s')),
                    "tags": {
                        "country": point.country,
                        "region": point.region,
                        "city": point.city,
                        "province": point.province,
                        "age_range": point.age_range
                    },
                    "fields": {
                        "females_deaths": point.females_deaths,
                        "males_deaths": point.males_deaths,
                        "total_deaths": point.total_deaths,
                        "age_range_field": point.age_range
                    },
                } for i, point in enumerate(chunk)
            ]
            self.influxdb_client.write_points(
                saving_points,
                database="covid19",
                time_precision="s"
            )
        return True

    def _save_covid_points(self, points: CovidPoint):
        saving_points = [
            {
                "measurement": point.source,
                "time": point.last_update,
                "tags": {
                    "country": point.country,
                    "region": point.region,
                    "city": point.city,
                },
                "fields": {
                    "confirmed_cumulative": point.confirmed_cumulative,
                    "hospitalized_cumulative": point.hospitalized_cumulative,
                    "severe_cumulative": point.severe_cumulative,
                    "death_cumulative": point.death_cumulative,
                    "recovered_cumulative": point.recovered_cumulative,
                    "tests_cumulative": point.tests_cumulative
                },
            } for i, point in enumerate(points)
        ]
        return self.influxdb_client.write_points(
            saving_points,
            database="covid19",
            time_precision="s"
        )

    def get_point_from_projection(self, projection_name: str, timestamp: int):
        query = 'select *, country, region, city from {} where time < {}'.format(
            projection_name, timestamp * 10**9
        )
        points = list(self.influxdb_client.query(query, epoch='s', database='covid19').get_points())
        return points and points[0] or None

    def get_points_from_projections(self, projection_name: str, tag, *tuples):
        points = []
        for chunk in chunks(tuples, 500):
            query = 'select *, time as time, country as country, region as region, city as city from '
            for i, tag_and_timestamp in enumerate(chunk):
                query += '(select *, time as time, country as country, region as region, city as city ' \
                         'from {} ' \
                         'where time < {} and {} = \'{}\' ' \
                         'order by time desc limit 1)'.format(
                    projection_name, tag_and_timestamp[1] * 10**9, tag, tag_and_timestamp[0]
                )
                query += ' order by time desc;' if i == len(chunk) - 1 else ','
            res = self.influxdb_client.query(query, epoch='s', database='covid19').get_points()
            points.extend(list(res))
        return points

    @staticmethod
    def _projection_to_influx_point(projection: typing.Dict, projection_name: str):
        p = {k: v for k, v in projection.items()}
        try:
            return {
                "measurement": projection_name,
                "time": p.pop('time'),
                "tags": {
                    "country": p.pop('country', ''),
                    "region": p.pop('region', ''),
                    "city": p.pop('city', ''),
                },
                "fields": p
            }
        except Exception as e:
            print('Error with projection: ', projection)
            raise e

    def save_projections(self, projection_name: str, *projections: typing.Dict):
        assert projections
        self.influxdb_client.write_points(
            [self._projection_to_influx_point(p, projection_name) for p in projections],
            database="covid19",
            time_precision="s"
        )
        return True

    def get_nearest_historical_points_by_fields(self, timestamp: int, source: str, field: str) \
            -> typing.List[CovidPoint]:
        assert isinstance(timestamp, int)
        query = "select *, country, region, city " \
                "from {} " \
                "where time < {} " \
                "group by {} order by desc limit 1".format(
            source, timestamp * 10**9, field
        )
        points = self.influxdb_client.query(query, epoch='s', database='covid19').get_points()
        res = [
            CovidPoint(
                source=source,
                timestamp=point['time'],
                last_update=point['time'],
                country=point['country'],
                region=point['region'],
                city=point['city'],
                confirmed_cumulative=point['confirmed_cumulative'],
                hospitalized_cumulative=point['hospitalized_cumulative'],
                severe_cumulative=point['severe_cumulative'],
                death_cumulative=point['death_cumulative'],
                recovered_cumulative=point['recovered_cumulative'],
                tests_cumulative=point.get('tests_cumulative', 0)
            ) for point in points
        ]
        return res

    def get_first_update_for_source(self, source: str) -> typing.Optional[int]:
        query = "select * from {} order by asc limit 1".format(source)
        res = list(self.influxdb_client.query(
            query,
            epoch='s',
            database='covid19'
        ).get_points())
        return res and int(res[0]['time']) or 0

    def get_last_update_for_source(self, source: str) -> typing.Optional[int]:
        query = "select * from {} order by time desc limit 1".format(source)
        res = list(self.influxdb_client.query(
            query,
            epoch='s',
            database='covid19'
        ).get_points())
        return res and int(res[0]['time']) or 0

    def delete_points_for_source(self, source, starts_from: int = 0) -> typing.Optional[int]:
        query = "delete from {} where time >= {}".format(source, starts_from)
        self.influxdb_client.query(
            query,
            epoch='s',
            database='covid19'
        )
        return True

    def delete_points_for_projection(self, projection_name, starts_from: int = 0, to: int = 0) -> typing.Optional[int]:
        query = "delete from {} where time >= {} and time < {}".format(
            projection_name, starts_from*10**9, to*10**9
        )
        print(query)
        self.influxdb_client.query(
            query,
            epoch='s',
            database='covid19'
        )
        return True
