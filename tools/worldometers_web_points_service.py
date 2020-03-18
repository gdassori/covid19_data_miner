import time
import typing
import datetime
import requests
from bs4 import BeautifulSoup


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
        for tid in ('table3', 'main_table_countries', 'main_table_countries_today'):
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
