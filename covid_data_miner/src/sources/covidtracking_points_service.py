import csv
import datetime
import typing

import requests

from covid_data_miner.src.domain import CovidPoint


class CovidTrackingUSAPointsService:
    country = 'USA'
    source_type = 'regional'
    source_name = 'covidtracking.com (CDC)'

    def __init__(self, authentication_key):
        self._ = authentication_key

    tags = ['region']

    def _fetch_data(self):
        return requests.get('http://covidtracking.com/api/states/daily.csv').content.decode()

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
            if 'date' == row[0].strip():
                continue
            updated_at = datetime.datetime.strptime(row[7], '%Y-%m-%dT%H:%M:%SZ')
            if min_timestamp and updated_at < datetime.datetime.fromtimestamp(min_timestamp):
                continue
            point = CovidPoint(
                source="covidtracking_usa",
                timestamp=updated_at,
                last_update=int(updated_at.strftime('%s')),
                country="USA",
                region=row[1].replace("'", "."),
                city="",
                confirmed_cumulative=int(row[2] or 0),
                death_cumulative=int(row[5] or 0),
                recovered_cumulative=0,
                hospitalized_cumulative=0,
                severe_cumulative=0,
                tests_cumulative=int(row[6] or 0)
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
            dt = datetime.datetime.strptime(_csv[1][7], '%Y-%m-%dT%H:%M:%SZ')
        except Exception as e:
            print(e)
            dt = None
        return dt and int(dt.strftime('%s'))


if __name__ == '__main__':
    s = CovidTrackingUSAPointsService()
    print(s.get_points_since(s.get_last_update()))
