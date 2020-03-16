import csv
import datetime
import typing

from github import Github
import base64

from covid_data_miner.src.domain import CovidPoint


class CSSEGISandDataPointsService:
    country = 'World'
    source_type = 'global'
    source_name = 'CSSE (JHU)'

    tags = ['country']

    def __init__(self, authentication_key):
        self.repo_name = 'CSSEGISandData/COVID-19'
        self.folder = '/csse_covid_19_data/csse_covid_19_daily_reports/'
        self.repo = Github(login_or_token=authentication_key, per_page=1000)

    @staticmethod
    def _filename_to_datetime(filename):
        filedate = filename.replace('.csv', '') + 'T00:00'
        d = datetime.datetime.strptime(filedate, '%m-%d-%YT%M:%S')
        return d

    def _fetch_data(self, starts_from):
        starts_from = starts_from - (starts_from % 86400)
        starts_from = datetime.datetime.fromtimestamp(starts_from)
        repo = self.repo.get_repo(self.repo_name)
        contents = repo.get_contents(self.folder)
        data = []
        for content in contents:
            if '.csv' not in content.name:
                continue
            date = self._filename_to_datetime(content.name)
            if date >= starts_from:
                entry = base64.b64decode(content.content).decode()
                data.append([date, entry])
        return data

    @staticmethod
    def _parse_csv(entry: str):
        res = []
        for row in csv.reader([x for x in entry.split('\n') if x], delimiter=','):
            res.append(row)
        return res

    @staticmethod
    def _get_last_update_timestamp(last_update: str) -> int:
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%m/%d/%y %H:%M',
            '%m/%d/%Y %H:%M'
        ]
        for i, dformat in enumerate(formats):
            try:
                return int(datetime.datetime.strptime(last_update, dformat).strftime('%s'))
            except ValueError as e:
                if i == len(formats) - 1:
                    raise e

    def _get_points(self, data: typing.List[typing.List]) -> typing.List[CovidPoint]:
        res = []
        for entry in data:
            rows = self._parse_csv(entry[1])
            for row in rows[1:]:
                last_update = self._get_last_update_timestamp(row[2])
                point = CovidPoint(
                    source="csse",
                    timestamp=entry[0],
                    last_update=last_update,
                    country=row[1],
                    region="",
                    city="",
                    confirmed_cumulative=int(row[3] or 0),
                    death_cumulative=int(row[4] or 0),
                    recovered_cumulative=int(row[5] or 0),
                    hospitalized_cumulative=0,
                    severe_cumulative=0,
                    tests_cumulative=0
                )
                res.append(point)
        return res

    def get_points_since(self, timestamp: int) -> typing.List[CovidPoint]:
        data = self._fetch_data(timestamp)
        return self._get_points(data)

    def get_latest(self):
        raise NotImplementedError
