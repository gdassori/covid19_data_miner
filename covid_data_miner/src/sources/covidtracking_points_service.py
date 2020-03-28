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
        return requests.get('http://covidtracking.com/api/states/daily').json()

    def _get_points(self, data: typing.List[typing.Dict], min_timestamp=None) -> typing.List[CovidPoint]:
        res = []
        for entry in data:
            updated_at = datetime.datetime.strptime(entry['dateChecked'], '%Y-%m-%dT%H:%M:%SZ')
            if min_timestamp and updated_at < datetime.datetime.fromtimestamp(min_timestamp):
                continue
            point = CovidPoint(
                source="covidtracking_usa",
                timestamp=updated_at,
                last_update=int(updated_at.strftime('%s')),
                country="USA",
                region=entry['state'].replace("'", "."),
                city="",
                confirmed_cumulative=int(entry['total'] or 0),
                death_cumulative=int(entry['death'] or 0),
                recovered_cumulative=entry['negative'] or 0,
                hospitalized_cumulative=int(entry['hospitalized'] or 0),
                severe_cumulative=0,
                tests_cumulative=int(entry['totalTestResults'] or 0)
            )
            res.append(point)
        return res

    def get_points_since(self, timestamp: int):
        data = self._fetch_data()
        points = self._get_points(data, timestamp)
        return points

    def get_last_update(self) -> int:
        data = self._fetch_data()
        try:
            dt = datetime.datetime.strptime(data[0]['dateChecked'], '%Y-%m-%dT%H:%M:%SZ')
        except Exception as e:
            print(e)
            dt = None
        return dt and int(dt.strftime('%s'))


if __name__ == '__main__':
    s = CovidTrackingUSAPointsService()
    print(s.get_points_since(s.get_last_update()))
