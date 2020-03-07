import abc
import datetime
import typing


class BaseProjection(metaclass=abc.ABCMeta):
    def __init__(self):
        self._normalizers = {}
        self.observers = []

    @staticmethod
    def _to_influxtime(dtime: datetime.datetime) -> int:
        dtime = int(dtime.strftime('%s'))
        return dtime * 10**9

    @abc.abstractmethod
    def rewind(self, since: int = None):
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
