import csv
import datetime
import typing
from github import Github
import base64

from covid_data_miner.src.domain import CovidPoint


class RkiDeGithubPointsService:
    country = 'Germany'
    source_type = 'regional'
    source_name = 'Robert Koch Institute'
    summary_projection = True

    tags = ['region']

    def __init__(self, authentication_key):
        self.repo_name = 'gdassori/covid19_data'
        self.folder = '/data/rki-de/'
        self.repo = Github(login_or_token=authentication_key or None, per_page=1000)

    @staticmethod
    def _filename_to_datetime(filename):
        filedate = filename.replace('.csv', '') + '150000'
        d = datetime.datetime.strptime(filedate, '%Y%m%d%H%M%S')
        return d

    def _fetch_data(self, starts_from):
        start_datetime = datetime.datetime.fromtimestamp(starts_from)
        start_folder = start_datetime.strftime('%Y%m')
        repo = self.repo.get_repo(self.repo_name)
        contents = repo.get_contents(self.folder)
        data = []
        for content in contents:
            if not content.name.isdigit():
                continue
            if content.name < start_folder:
                continue
            files = repo.get_contents(self.folder + content.name + '/')
            for f in files:
                if '.csv' not in f.name:
                    continue
                date = self._filename_to_datetime(f.name)
                if date >= start_datetime:
                    entry = base64.b64decode(f.content).decode()
                    data.append([date, entry])
        return data

    @staticmethod
    def _parse_csv(entry: str):
        res = []
        for row in csv.reader([x for x in entry.split('\n') if x], delimiter=','):
            res.append(row)
        return res

    def _get_points(self, data: typing.List[typing.List], min_timestamp=None) -> typing.List[CovidPoint]:
        res = []
        for entry in data:
            updated_at, rows = entry
            rows = self._parse_csv(rows)
            for row in rows:
                if min_timestamp and updated_at < datetime.datetime.fromtimestamp(min_timestamp):
                    continue
                if 'undesland' in row[0] or 'tate' in row[0] or 'esamt' in row[0]:
                    continue
                point = CovidPoint(
                    source="rki_de",
                    timestamp=updated_at,
                    last_update=int(updated_at.strftime('%s')),
                    country="Germany",
                    region=row[0],
                    city="",
                    confirmed_cumulative=int(row[1].replace('.', '').strip() or 0),
                    death_cumulative=int(row[2].replace('.', '').strip() if len(row) > 2 and row[2] else 0),
                    recovered_cumulative=0,
                    hospitalized_cumulative=0,
                    severe_cumulative=0,
                    tests_cumulative=0
                )
                res.append(point)
        return res

    def get_points_since(self, timestamp: int):
        data = self._fetch_data(timestamp)
        points = self._get_points(data, timestamp)
        return points

    def get_last_update(self) -> int:
        repo = self.repo.get_repo(self.repo_name)
        f = repo.get_contents(self.folder + 'updated_at')
        return f.content and int(base64.b64decode(f.content).decode())


if __name__ == '__main__':
    s = RkiDeGithubPointsService(None)
    p = s.get_points_since(0)
    print(p)
