import csv
import datetime
import typing

import requests

from covid_data_miner.src.domain import CovidPoint, IstatDeathRatePoint, InhabitantsPoint
from covid_data_miner.src.utils import normalize_data


class WorldInhabitantsPointsService:
    country = 'World'
    source_type = 'regional'
    source_name = 'World Inhabitants - Aggregated data from multiple sources'
    summary_projection = False

    tags = ['region', 'province']

    def __init__(self, authentication_key):
        self._country_fns = {
            'Italy': self._get_italy_inhabitants
        }

    def _get_italy_inhabitants(self):
        data = requests.get(
            'https://raw.githubusercontent.com/gdassori/covid19_data/'
            'master/data/world_inhabitants/abitanti_province_italia.csv'
        ).content.decode()
        res = []
        data = self._parse_csv(data)
        for entry in data[1:]:
            res.append(
                {
                    'country': 'Italy',
                    'province': entry[0],
                    'region': entry[1],
                    'residents': entry[2],
                    'size_sqm': entry[3],
                    'density': entry[4],
                    'municipalities': entry[5],
                    'timestamp': datetime.datetime.strptime(entry[6], '%Y-%m-%d'),
                }
            )
        return res

    @staticmethod
    def _parse_csv(entry: str):
        res = []
        for row in csv.reader([x for x in entry.split('\n') if x], delimiter=','):
            res.append(row)
        return res

    def _get_points(self, timestamp=None) -> typing.List[CovidPoint]:
        res = []
        for country, function in self._country_fns.items():
            data = function()
            for d in data:
                if timestamp <= int(d['timestamp'].strftime('%s')):
                    res.append(
                        InhabitantsPoint(
                            timestamp=d['timestamp'],
                            country=d['country'],
                            province=normalize_data(d['province']),
                            region=normalize_data(d['region']),
                            residents=int(d['residents']),
                            size_sqm=float(d['size_sqm']),
                            density=int(d['density']),
                            municipalities=int(d['municipalities'])
                        )
                    )
        return res

    def get_points_since(self, timestamp: int):
        points = self._get_points(timestamp)
        return points

    def get_last_update(self) -> int:
        last_updates = self._parse_csv(requests.get(
            'https://raw.githubusercontent.com/gdassori/covid19_data/master/data/world_inhabitants/last_updates'
        ).content.decode())
        d = []
        for l in last_updates[1:]:
            d.append(
                int(datetime.datetime.strptime(l[2].strip(), '%Y-%m-%dT%H:%M:%S').strftime('%s'))
            )
        return max(d)


if __name__ == '__main__':
    s = WorldInhabitantsPointService(None)
    print(len(s.get_points_since(s.get_last_update())))
