import csv
import datetime
import typing

import requests

from covid_data_miner.src.domain import CovidPoint, IstatDeathRatePoint


class IstatWeeklyDeathsGithubPointsService:
    country = 'Italy'
    source_type = 'regional'
    source_name = 'Istat - Weekly Italy Death Rate'
    summary_projection = False

    tags = ['region', 'city']

    def __init__(self, authentication_key):
        pass

    @staticmethod
    def _weekref_to_datetime(row, year):
        week_end = row[6].split('-')[1]
        stuff = '{}/{}T23:59:59'.format(week_end, year)
        try:
            return datetime.datetime.strptime(stuff, '%d/%m/%YT%H:%M:%S')
        except ValueError as e:
            if str(e) == 'day is out of range for month':
                if week_end == '29/02':
                    stuff = '28/02/{}T23:59:59'.format(year)
                    return datetime.datetime.strptime(stuff, '%d/%m/%YT%H:%M:%S')
            raise e

    @staticmethod
    def _parse_csv(entry: str):
        res = []
        for row in csv.reader([x for x in entry.split('\n') if x], delimiter=','):
            res.append(row)
        return res

    @staticmethod
    def _get_years(index):
        data = {}
        for i, entry in enumerate(index):
            v = entry.split('_')
            if len(v) == 2 and v[1].isdigit():
                if not data.get(v[1]):
                    data[v[1]] = {v[0].lower(): i}
                else:
                    data[v[1]][v[0].lower()] = i
        return data

    def _get_points(self, data: str, timestamp=None) -> typing.List[CovidPoint]:
        res = []
        data = self._parse_csv(data)
        index = data[0]
        years = self._get_years(index)
        for row in data[1:]:
            for year, yeardata in years.items():
                point = IstatDeathRatePoint(
                    source="istat_weekly_death_rate",
                    country='Italy',
                    age_range=row[7],
                    region=row[3],
                    province=row[4],
                    city=row[5],
                    timestamp=self._weekref_to_datetime(row, year),
                    females_deaths=int(row[yeardata['femmine']]),
                    males_deaths=int(row[yeardata['maschi']]),
                    total_deaths=int(row[yeardata['totale']])
                )
                res.append(point)
        return res

    def get_points_since(self, timestamp: int):
        data = requests.get(
            'https://raw.githubusercontent.com/gdassori/covid19_data/master/' +
            'data/istat/mortalita_comuni_italia_settimanale_istat_2020.csv'
        ).content.decode()
        points = self._get_points(data, timestamp)
        return points

    def get_last_update(self) -> int:
        return int(requests.get(
            'https://raw.githubusercontent.com/gdassori/covid19_data/' +
            'master/data/istat/mortalita_comuni_italia_settimanale_updated_at'
        ).content.decode())


if __name__ == '__main__':
    s = IstatWeeklyDeathsGithubPointsService(None)
    print(len(s.get_points_since(s.get_last_update())))
