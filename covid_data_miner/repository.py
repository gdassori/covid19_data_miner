import abc
import datetime
import threading
import influxdb as influxdb
from influxdb import InfluxDBClient

from covid_data_miner.domain import CovidPoint


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
        self.databases = ['historical_data']
        self.influxdb_client.ping()

    def save_historical_points(self, *points: CovidPoint):
        saving_points = [
            {
                "measurement": point.source,
                "time": point.last_update * 1000000 + i,
                "tags": {
                    "source": point.source,
                    "country": point.country,
                    "province": point.province,
                    "day": int(point.timestamp.strftime('%s')),
                    "lat": 0,
                    "lon": 0,
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
