import csv
import os
from covid_data_miner.service.worldometers_points_service import WorldometersPointsService

if __name__ == '__main__':
    w = WorldometersPointsService()

    #starts_at = int(datetime.datetime.strptime('2020-01-10', '%Y-%m-%d').strftime('%s'))
    #starts_at = starts_at - (starts_at % 21600)
    #csvs = w.fetch_since(starts_at)

    csvs = [w.fetch_current()]
    for updated_at, data in csvs:
        if not updated_at[:6] in os.listdir('data/worldometers.info'):
            os.mkdir('data/worldometers.info/{}'.format(updated_at[:6]))
        with open('data/worldometers.info/{}/{}.csv'.format(updated_at[:6], updated_at), 'w') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for i, row in enumerate(data):
                if not i:
                    row = [x.replace(',', '/') for x in row]
                else:
                    row = [x.replace(',', '').replace('+', '') for x in row]
                if 'total' in row[0].lower():
                    continue
                writer.writerow(row)
