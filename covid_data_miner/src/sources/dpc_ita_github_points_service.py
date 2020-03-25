import csv
import datetime
import typing
from github import Github
import base64

from covid_data_miner.src.domain import CovidPoint


class DPCItaGithubPointsService:
    country = 'Italy'
    source_type = 'regional'
    source_name = 'Dipartimento Protezione Civile'

    tags = ['region']

    def __init__(self, authentication_key):
        self.repo_name = 'pcm-dpc/COVID-19'
        self.folder = '/dati-regioni/'
        self.repo = Github(login_or_token=authentication_key or None, per_page=1000)

    @staticmethod
    def _filename_to_datetime(filename):
        filedate = filename.replace('.csv', '')
        d = datetime.datetime.strptime(filedate, '%Y%m%d%H%M%S')
        return d

    def _fetch_data(self):
        repo = self.repo.get_repo(self.repo_name)
        content = repo.get_contents(self.folder + 'dpc-covid19-ita-regioni.csv')
        return base64.b64decode(content.content).decode()

    @staticmethod
    def _parse_csv(entry: str):
        res = []
        for row in csv.reader([x for x in entry.split('\n') if x], delimiter=','):
            res.append(row)
        return res

    def _get_points(self, data: str, min_timestamp=None) -> typing.List[CovidPoint]:
        res = []
        rows = self._parse_csv(data)
        for row in rows:
            if 'data' == row[0]:
                continue
            dt_format = '%Y-%m-%dT%H:%M:%S' if 'T' in row[0] else '%Y-%m-%d %H:%M:%S'
            updated_at = datetime.datetime.strptime(row[0], dt_format)
            if min_timestamp and updated_at < datetime.datetime.fromtimestamp(min_timestamp):
                continue
            point = CovidPoint(
                source="dpc_ita",
                timestamp=updated_at,
                last_update=int(updated_at.strftime('%s')),
                country="Italy",
                region=row[3].replace("'", "."),
                city="",
                confirmed_cumulative=int(row[14]),
                death_cumulative=int(row[13]),
                recovered_cumulative=int(row[12]),
                hospitalized_cumulative=int(row[8]),
                severe_cumulative=int(row[7]),
                tests_cumulative=int(row[15])
            )
            res.append(point)
        return res

    def get_points_since(self, timestamp: int):
        data = self._fetch_data()
        points = self._get_points(data, timestamp)
        return points

    def get_last_update(self) -> int:
        data = self._fetch_data()
        _csv = self._parse_csv(data)
        try:
            dt_format = '%Y-%m-%dT%H:%M:%S' if 'T' in _csv[-1][0] else '%Y-%m-%d %H:%M:%S'
            dt = datetime.datetime.strptime(_csv[-1][0], dt_format)
        except Exception as e:
            print(e)
            dt = None
        return dt and int(dt.strftime('%s'))


if __name__ == '__main__':
    s = DPCItaGithubPointsService(None)
    print(s.get_points_since(s.get_last_update()))
