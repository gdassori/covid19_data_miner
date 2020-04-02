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
    summary_projection = True

    tags = ['country', 'region']

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
        """
        output: [timestamp, country, region, confirmed, death, recovered]
        """
        _res = []
        res = []
        for row in csv.reader([x for x in entry.split('\n') if x], delimiter=','):
            _res.append(row)
        _res[0][0] = _res[0][0].replace('\ufeff', '')
        if _res[0] in [
            [
                'Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered'
            ],
            [
                'Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered'
            ],
            [
                'Province/State', 'Country/Region', 'Last Update',
                'Confirmed', 'Deaths', 'Recovered', 'Latitude', 'Longitude'
            ],
        ]:
            for r in _res[1:]:
                res.append([r[2], r[1].replace("'", "."), r[0].replace("'", "."), r[3], r[4], r[5]])
        elif _res[0] in [
            [
                'FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Last_Update', 
                'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'Combined_Key'
            ]
        ]:
            for r in _res[1:]:
                res.append([r[4], r[3].replace("'", "."), r[2].replace("'", "."), r[7], r[8], r[9]])
        else:
            print('Error with row: %s' % _res[0])
            raise ValueError(_res[0])
        return res

    @staticmethod
    def _get_last_update_timestamp(last_update: str) -> int:
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
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
            for row in rows:
                last_update = self._get_last_update_timestamp(row[0])
                point = CovidPoint(
                    source="csse",
                    timestamp=datetime.datetime.fromtimestamp(last_update),
                    last_update=last_update,
                    country=row[1],
                    region=row[2],
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

    def get_last_update(self) -> int:
        repo = self.repo.get_repo(self.repo_name)
        contents = repo.get_contents(self.folder)
        last_date = None
        for content in contents:
            if '.csv' not in content.name:
                continue
            date = self._filename_to_datetime(content.name)
            last_date = date if last_date and date > last_date else date if not last_date else last_date
        return last_date and int(last_date.strftime('%s'))
