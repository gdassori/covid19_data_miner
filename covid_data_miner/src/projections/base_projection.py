import abc
import datetime
import typing

from covid_data_miner.src.utils import influxdb_repository_factory


class BaseProjection(metaclass=abc.ABCMeta):
    def __init__(self, repository_factory=influxdb_repository_factory):
        self._normalizers = {}
        self.observers = []
        self.influxdb_factory = repository_factory
        self._repository = None

    @property
    def repository(self):
        if not self._repository:
            self._repository = self.influxdb_factory()
        return self._repository

    @staticmethod
    def _to_influxtime(dtime: datetime.datetime) -> int:
        dtime = int(dtime.strftime('%s'))
        return dtime * 10**9

    @abc.abstractmethod
    def rewind(self, since: datetime.datetime = None, disable_plugins: bool = False):
        pass

    @abc.abstractmethod
    def project(self, data: typing.List[typing.Dict]):
        pass

    def add_value_normalizer(self, field, value, target):
        self._normalizers[field][value] = target

    def _normalize_key(self, field: str, value: str) -> str:
        try:
            return self._normalizers[field][value]
        except KeyError:
            return value

    def add_observer(self, observer):
        self.observers.append(observer)
