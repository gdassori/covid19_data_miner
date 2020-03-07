import abc
import threading
import typing

import influxdb as influxdb
from influxdb import InfluxDBClient

from covid_data_miner.src.domain import CovidPoint


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
        self.databases = ['historical_data', 'projections']
        self.influxdb_client.ping()

    def save_historical_points(self, *points: CovidPoint):
        print('Saving', len(points), 'points')
        saving_points = [
            {
                "measurement": point.source,
                "time": point.last_update * 1000000 + i,
                "tags": {
                    "country": point.country,
                    "province": point.province,
                    "city": point.city
                },
                "fields": {
                    "confirmed_cumulative": point.confirmed_cumulative,
                    "hospitalized_cumulative": point.hospitalized_cumulative,
                    "severe_cumulative": point.severe_cumulative,
                    "death_cumulative": point.death_cumulative,
                    "recovered_cumulative": point.recovered_cumulative
                },
            } for i, point in enumerate(points)
        ]
        return self.influxdb_client.write_points(
            saving_points,
            database="historical_data",
            time_precision="u"
        )

    def get_projection(self, measurement: str, time: int):
        pass

    def get_projections_with_timestamps(self, measurement: str, *timestamps):
        pass

    def save_projections(self, measurement: str, *projections: typing.Dict):
        return self.influxdb_client.write_points(
            projections,
            database="projections",
            time_precision="u"
        )

    def get_nearest_historical_points_by_fields(self, timestamp: int, measurement: str, field: str) \
            -> typing.List[CovidPoint]:
        assert isinstance(timestamp, int)
        timestamp *= 10**9
        query = "select * from {} where time < {} group by {} order by desc limit 1;".format(
            measurement, timestamp, field
        )

    def get_first_historical_point_time_for_measurement(self, measurement: str):
        query = "select time from {} order by asc limit 1;".format(
            measurement
        )
        # time_precision='s'
