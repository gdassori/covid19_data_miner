import time
import typing
import datetime
import requests
from bs4 import BeautifulSoup

from covid_data_miner.domain import CovidPoint


class WorldometersWebPointsService:
    def __init__(self, interval=21600):
        self.interval = interval  # 6 hours
        self.nearest_template = 'https://archive.org/wayback/available?timestamp={}' \
                                '&url=https://www.worldometers.info/coronavirus/'

    def _get_datestrings_since_timestamp(self, timestamp) -> typing.List[str]:
        now = int(time.time())
        now = now - (now % self.interval)
        dates = range(timestamp, now, self.interval)
        return [
            datetime.datetime.fromtimestamp(d).strftime('%Y%m%d%H%M%S') for d in dates
        ]

    def _snapshots_to_csv(self, snapshot) -> typing.Optional[typing.List]:
        soup = BeautifulSoup(snapshot)
        table = None
        for tid in ('table3', 'main_table_countries'):
            table = table or soup.find(id=tid)
        if not table:
            return
        output_rows = []
        for i, table_row in enumerate(table.findAll('tr')):
            if not i:
                columns = table_row.findAll('th')
                assert columns
                output_row = []
                for column in columns:
                    output_row.append(column.text.strip())
                output_rows.append(output_row)
            else:
                columns = table_row.findAll('td')
                assert columns
                output_row = []
                for column in columns:
                    output_row.append(column.text.strip())
                output_rows.append(output_row)
        return output_rows

    def _fetch_nearest_snapshot(self, datestring: str, already_saved=[]):
        url = self.nearest_template.format(datestring)
        snapshot = requests.get(url).json()
        closest = snapshot.get('archived_snapshots', {}).get('closest', {}).get('url')
        if not closest:
            return
        timestamp = closest \
            .replace('http://web.archive.org/web/', '') \
            .replace('/https://www.worldometers.info/coronavirus/', '')
        if timestamp in already_saved:
            print('Timestamp %s already saved' % timestamp)
            print('Snapshot: %s' % snapshot)
            return
        already_saved.append(timestamp)
        return [closest, requests.get(closest).content, timestamp]

    def fetch_since(self, timestamp: int):
        now = int(time.time())
        now = now - (now % self.interval)
        assert timestamp < now, 'timestamp must be < now'
        assert not timestamp % self.interval, 'timestamp must be multiple of {}'.format(self.interval)
        datestrings = self._get_datestrings_since_timestamp(timestamp)
        snapshots = []
        already_saved = []
        for datestring in datestrings:
            data = self._fetch_nearest_snapshot(datestring, already_saved=already_saved)
            if not data:
                print('No match for datestring', datestring)
                continue
            url, raw_snapshots, updated_at = data
            csv = self._snapshots_to_csv(raw_snapshots)
            if csv:
                print('Saved csv at', updated_at)
                snapshots.append([updated_at, csv])
            else:
                print('Failure with url', url)
        return snapshots

    def fetch_current(self):
        now = int(time.time())
        data = requests.get('https://www.worldometers.info/coronavirus/').content
        csv = self._snapshots_to_csv(data)
        updated_at = datetime.datetime.fromtimestamp(now).strftime('%Y%m%d%H%M%S')
        return [updated_at, csv]
    
    def _get_points_from_csv_v1(self, rows):
        # Country,Cases,Deaths,Region
        h = rows[0]
        assert all([
            'ountr' in h[0], 'ases' in h[1], 'eath' in h[2], 'egion' in h[3],
        ]), h
        return [[r[0], r[1], r[2], '', ''] for r in rows[1:]]

    def _get_points_from_csv_v2(self, rows):
        # Country,Total Cases,Change Today,Total Deaths,Region
        h = rows[0]
        assert all([
            'ountr' in h[0], 'ases' in h[1], 'eath' in h[3], 'egion' in h[4]   
        ]), rows[0]
        return [[r[0], r[1], r[3], '', ''] for r in rows[1:]]

    def _get_points_from_csv_v3(self, rows):
        # Country,Total Cases,New Today,Total Deaths,Today's Deaths,Total Cured,Total Critical,Region
        h = rows[0]
        assert all([
            'ountry' in h[0], 'otal' in h[1], 'ases' in h[1],
            'otal' in h[3], 'eath' in h[3], any(['ured' in h[5], 'ered' in h[5]]), 'otal' in h[5],
            any(['ritical' in h[6], 'evere' in h[6]]), 'egion' in h[7]
        ]), rows[0]
        return [[r[0], r[1], r[3], r[5], r[6]] for r in rows[1:]]

    def _get_points_from_csv_v4(self, rows):
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

    def _get_points(self, data: typing.List[typing.List]) -> typing.List[CovidPoint]:
        res = []
        for entry in data:
            last_update, rows = entry
            if len(rows[0]) == 4:
                # Country,Cases,Deaths,Region
                rows = self._get_points_from_csv_v1(rows)
            elif len(rows[0]) == 5:
                # Country,Total Cases,Change Today,Total Deaths,Region
                rows = self._get_points_from_csv_v2(rows)
            elif len(rows[0]) in (8, 7):
                # Country,Total Cases,New Today,Total Deaths,Today's Deaths,Total Cured,Total Critical,Region
                rows = self._get_points_from_csv_v3(rows)
            timestamp = datetime.datetime.strptime(last_update, '%Y%m%d%H%M%S')
            for row in rows:
                if 'ases' in row[1]:
                    continue
                try:
                    point = CovidPoint(
                        source="worldometers",
                        timestamp=timestamp,
                        last_update=int(timestamp.strftime('%s')),
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
        data = self.fetch_since(timestamp)
        points = self._get_points(data)
        return points

    def get_current_point(self):
        data = self.fetch_current()
        points = self._get_points([data])[0]
        return points
