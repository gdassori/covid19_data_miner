import csv
import datetime
import typing

import requests

from covid_data_miner.src.domain import CovidPoint, IstatDeathRatePoint
from covid_data_miner.src.utils import normalize_data


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

    @staticmethod
    def _ensure_data_populated(data, region, province, timestamp):
        template = {
            "females_deaths": 0,
            "males_deaths": 0,
            "total_deaths": 0,
            "females_0_14_deaths": 0,
            "males_0_14_deaths": 0,
            "total_0_14_deaths": 0,
            "females_15_64_deaths": 0,
            "males_15_64_deaths": 0,
            "total_15_64_deaths": 0,
            "females_65_74_deaths": 0,
            "males_65_74_deaths": 0,
            "total_65_74_deaths": 0,
            "females_over75_deaths": 0,
            "males_over75_deaths": 0,
            "total_over75_deaths": 0,
        }
        if not data.get(region):
            data[region] = {province: {timestamp: template}}
        elif not data[region].get(province):
            data[region][province] = {timestamp: template}
        elif not data[region][province].get(timestamp):
            data[region][province][timestamp] = template

    @staticmethod
    def _get_range_key(range):
        return {
            '0-14 anni': '0_14',
            '15-64 anni': '15_64',
            '65-74 anni': '65_74',
            '75 anni e più': 'over75'
        }[range]

    def _get_points(self, data: str, timestamp=None) -> typing.List[CovidPoint]:
        res = []
        csv_data = self._parse_csv(data)
        index = csv_data[0]
        years = self._get_years(index)
        pre_res = {}
        for row in csv_data[1:]:
            for year, yeardata in years.items():
                timestamp = self._weekref_to_datetime(row, year)
                key = self._get_range_key(row[7])
                self._ensure_data_populated(pre_res, row[3], row[4], timestamp)
                pre_res[row[3]][row[4]][timestamp]['females_deaths'] += int(row[yeardata['femmine']])
                pre_res[row[3]][row[4]][timestamp]['males_deaths'] += int(row[yeardata['maschi']])
                pre_res[row[3]][row[4]][timestamp]['total_deaths'] += int(row[yeardata['totale']])
                pre_res[row[3]][row[4]][timestamp]['females_{}_deaths'.format(key)] += int(row[yeardata['femmine']])
                pre_res[row[3]][row[4]][timestamp]['males_{}_deaths'.format(key)] += int(row[yeardata['maschi']])
                pre_res[row[3]][row[4]][timestamp]['total_{}_deaths'.format(key)] += int(row[yeardata['totale']])
        for region in pre_res.keys():
            for province in pre_res[region].keys():
                for timestamp, _data in pre_res[region][province].items():
                    res.append(
                        IstatDeathRatePoint(
                            timestamp=timestamp,
                            country='Italy',
                            province=normalize_data(province),
                            region=normalize_data(region),
                            city='',
                            females_deaths=_data['females_deaths'],
                            males_deaths=_data['males_deaths'],
                            total_deaths=_data['total_deaths'],
                            females_0_14_deaths=_data['females_0_14_deaths'],
                            males_0_14_deaths=_data['males_0_14_deaths'],
                            total_0_14_deaths=_data['total_0_14_deaths'],
                            females_15_64_deaths=_data['females_15_64_deaths'],
                            males_15_64_deaths=_data['males_15_64_deaths'],
                            total_15_64_deaths=_data['total_15_64_deaths'],
                            females_65_74_deaths=_data['females_65_74_deaths'],
                            males_65_74_deaths=_data['males_65_74_deaths'],
                            total_65_74_deaths=_data['total_65_74_deaths'],
                            females_over75_deaths=_data['females_over75_deaths'],
                            males_over75_deaths=_data['males_over75_deaths'],
                            total_over75_deaths=_data['total_over75_deaths'],
                            source='istat_weekly_death_rate'
                        )
                    )
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
