import csv
import datetime
import typing

from github import Github
import base64

from covid_data_miner.src.domain import CovidPoint


class WorldometersGithubPointsService:
    tags = ['country']

    def __init__(self, authentication_key):
        self.repo_name = 'gdassori/covid19_data'
        self.folder = '/data/worldometers.info/'
        self.repo = Github(login_or_token=authentication_key, per_page=1000)


    @staticmethod
    def _filename_to_datetime(filename):
        filedate = filename.replace('.csv', '')
        d = datetime.datetime.strptime(filedate, '%Y%m%d%H%M%S')
        return d

    def _fetch_data(self, starts_from):
        start_datetime = datetime.datetime.fromtimestamp(starts_from)
        start_folder = start_datetime.strftime('%Y%m')
        repo = self.repo.get_repo(self.repo_name)
        contents = repo.get_contents(self.folder)
        data = []
        for content in contents:
            if not content.name.startswith(start_folder[:3]):
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

    @staticmethod
    def _get_points_from_csv_v1(rows):
        # Country,Cases,Deaths,Region
        h = rows[0]
        assert all([
            'ountr' in h[0], 'ases' in h[1], 'eath' in h[2], 'egion' in h[3],
            ]), h
        return [[r[0], r[1], r[2], '', ''] for r in rows[1:]]

    @staticmethod
    def _get_points_from_csv_v2(rows):
        # Country,Total Cases,Change Today,Total Deaths,Region
        h = rows[0]
        assert all([
            'ountr' in h[0], 'ases' in h[1], 'eath' in h[3], 'egion' in h[4]
        ]), rows[0]
        return [[r[0], r[1], r[3], '', ''] for r in rows[1:]]

    @staticmethod
    def _get_points_from_csv_v3(rows):
        # Country,Total Cases,New Today,Total Deaths,Today's Deaths,Total Cured,Total Critical,Region
        h = rows[0]
        assert all([
            'ountry' in h[0], 'otal' in h[1], 'ases' in h[1],
            'otal' in h[3], 'eath' in h[3], any(['ured' in h[5], 'ered' in h[5]]), 'otal' in h[5],
            any(['ritical' in h[6], 'evere' in h[6]])
        ]), rows[0]
        return [[r[0], r[1], r[3], r[5], r[6]] for r in rows[1:]]

    @staticmethod
    def _get_points_from_csv_v4(rows):
        # Country,Total Cases,New Today,Total Deaths,Today's Deaths,Total Cured,Total Critical,Region
        # Country/ Territory,Total Cases,New Cases,Total Deaths,NewDeaths,Total Recovered,Serious/  Critical,Region
        # Country/ Territory,Total Cases,New Cases,Total Deaths,NewDeaths,Total Recovered,Serious/  Critical
        h = rows[0]
        assert all([
            'ountry' in h[0], 'otal' in h[1], 'ases' in h[1],
            'otal' in h[3], 'eath' in h[3], any(['ured' in h[5], 'overed']), 'otal' in h[5],
            'otal' in h[6], any(['ritical' in h[6], 'severe' in h[6]])
        ]), rows[0]
        return [[r[0], r[1], r[3], r[5], r[6]] for r in rows[1:]]

    @staticmethod
    def _get_points_from_csv_v5(rows):
        # Country/Other, TotalCases, NewCases, TotalDeaths, NewDeaths, ActiveCases, TotalRecovered, Serious/Critical
        h = rows[0]
        assert all([
            'ountry' in h[0], 'otal' in h[1], 'ases' in h[1],
            'otal' in h[3], 'eath' in h[3], any(['ured' in h[6], 'overed']), 'otal' in h[6],
            any(['ritical' in h[7], 'severe' in h[7]])
        ]), rows[0]
        return [[r[0], r[1], r[3], r[6], r[7]] for r in rows[1:]]

    @staticmethod
    def _get_points_from_csv_v6(rows):
        # 'Country', 'Total Cases', 'Today', 'Total Deaths', 'Today', 'Region'
        h = rows[0]
        assert all([
            'ountry' in h[0], 'otal' in h[1], 'ases' in h[1], 'otal' in h[3], 'eath' in h[3]
        ]), rows[0]
        return [[r[0], r[1], r[3], '', ''] for r in rows[1:]]

    def _get_points(self, data: typing.List[typing.List]) -> typing.List[CovidPoint]:
        res = []
        for entry in data:
            updated_at, rows = entry
            rows = self._parse_csv(rows)
            error = False
            for v in range(1, 7):
                try:
                    parser = getattr(self, '_get_points_from_csv_v' + str(v))
                    rows = parser(rows)
                    error = False
                    break
                except (IndexError, AssertionError):
                    error = True
            if error:
                raise ValueError('Error parsing row: %s' % rows and rows[0])
            for row in rows:
                if 'ases' in row[1]:
                    continue
                try:
                    point = CovidPoint(
                        source="worldometers",
                        timestamp=updated_at,
                        last_update=int(updated_at.strftime('%s')),
                        country=row[0],
                        province="",
                        confirmed_cumulative=int(row[1].replace(',', '').strip() or 0),
                        death_cumulative=int(row[2].replace(',', '').strip() or 0),
                        recovered_cumulative=int(row[3].replace(',', '').strip() or 0),
                        hospitalized_cumulative=0,
                        severe_cumulative=int(row[4].replace(',', '').strip() or 0),
                        lat=0,
                        lon=0
                    )
                except:
                    raise
                res.append(point)
        return res

    def get_points_since(self, timestamp: int):
        data = self._fetch_data(timestamp)
        points = self._get_points(data)
        return points
