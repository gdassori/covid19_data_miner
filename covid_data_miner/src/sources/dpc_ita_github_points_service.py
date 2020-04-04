import datetime
import typing

import requests

from covid_data_miner.src.domain import CovidPoint
from covid_data_miner.src.utils import normalize_data


class DPCItaGithubPointsService:
    country = 'Italy'
    source_type = 'regional'
    source_name = 'Dipartimento Protezione Civile'
    summary_projection = True

    tags = ['region']

    def __init__(self, authentication_key):
        pass

    @staticmethod
    def _filename_to_datetime(filename):
        filedate = filename.replace('.csv', '')
        d = datetime.datetime.strptime(filedate, '%Y%m%d%H%M%S')
        return d

    def _get_points(self, data: typing.List[typing.Dict], min_timestamp=None) -> typing.List[CovidPoint]:
        res = []
        for row in data:
            dt_format = '%Y-%m-%dT%H:%M:%S' if 'T' in row['data'] else '%Y-%m-%d %H:%M:%S'
            updated_at = datetime.datetime.strptime(row['data'], dt_format)
            if min_timestamp and updated_at < datetime.datetime.fromtimestamp(min_timestamp):
                continue
            point = CovidPoint(
                source="dpc_ita",
                timestamp=updated_at,
                last_update=int(updated_at.strftime('%s')),
                country="Italy",
                region=normalize_data(row['denominazione_regione'].replace("'", ".")),
                city="",
                confirmed_cumulative=int(row['totale_positivi']),
                death_cumulative=int(row['deceduti']),
                recovered_cumulative=int(row['dimessi_guariti']),
                hospitalized_cumulative=int(row['totale_ospedalizzati']),
                severe_cumulative=int(row['terapia_intensiva']),
                tests_cumulative=int(row['tamponi'])
            )
            res.append(point)
        return res

    def get_points_since(self, timestamp: int):
        data = requests.get(
            'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json'
        ).json()
        points = self._get_points(data, timestamp)
        return points

    def get_last_update(self) -> int:
        data = requests.get(
            'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json'
        ).json()
        try:
            dt_format = '%Y-%m-%dT%H:%M:%S' if 'T' in data[-1]['data'] else '%Y-%m-%d %H:%M:%S'
            dt = datetime.datetime.strptime(data[-1]['data'], dt_format)
        except Exception as e:
            print(e)
            dt = None
        return dt and int(dt.strftime('%s'))


if __name__ == '__main__':
    s = DPCItaGithubPointsService(None)
    print(s.get_points_since(s.get_last_update()))
