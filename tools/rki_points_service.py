import typing
import datetime
import requests
from bs4 import BeautifulSoup


class RKIPointsService:
    def __init__(self, interval=86400):
        self.interval = interval

    def _snapshots_to_csv(self, snapshot) -> typing.Optional[typing.List]:
        soup = BeautifulSoup(snapshot)
        table = soup.find(lambda tag: tag.name == 'table')
        if not table:
            return
        output_rows = []
        for i, table_row in enumerate(table.findAll('tr')):
            if table_row.findAll('th'):
                columns = table_row.findAll('th')
                if columns and columns[0].contents and 'undesl' in columns[0].contents[0]:
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

    def _parse_row(self, row):
        state = row[0]
        if '(' in row[1]:
            confirmed, deaths = row[1].split(' ')
            confirmed = str(int(confirmed.replace('.', '').strip()))
            deaths =    str(int(deaths.replace('(', '').replace(')', '').replace('.', '').strip()))
            assert confirmed and deaths
        else:
            confirmed = str(int(row[1].replace('.', '').strip()))
            assert confirmed
            deaths = '0'
        return [state, confirmed, deaths]

    def fetch_current(self):
        res = requests.get('https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html')
        res.raise_for_status()
        data = res.content
        csv = self._snapshots_to_csv(data)
        assert 'undesl' in csv[0][0]
        data = [['State', 'Confirmed', 'Deaths']]
        for l in csv[1:]:
            data.append(self._parse_row(l))
        return datetime.datetime.now().strftime('%Y%m%d'), data
