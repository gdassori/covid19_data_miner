import shutil
import csv
import os
from covid_data_miner.service.worldometers_web_points_service import WorldometersWebPointsService
import sys

if __name__ == '__main__':
    args = sys.argv
    prefix = './data'
    if len(args) > 1:
        if args[1] != '-o' or not args[2]:
            print('usage: -o /output/directory')
            exit(1)
        try:
            assert os.listdir(args[2])
        except (FileNotFoundError, NotADirectoryError) as e:
            print('Error with path', args[2], str(e))
            exit(1)
        prefix = args[2].rstrip('/')

    w = WorldometersWebPointsService()

    #starts_at = int(datetime.datetime.strptime('2020-01-10', '%Y-%m-%d').strftime('%s'))
    #starts_at = starts_at - (starts_at % 21600)
    #csvs = w.fetch_since(starts_at)

    csvs = [w.fetch_current()]
    filename = None
    for updated_at, data in csvs:
        #if not updated_at[:6] in os.listdir('{}/data/worldometers.info'.format(prefix)):
        os.makedirs('{}/worldometers.info/{}'.format(prefix, updated_at[:6]), exist_ok=True)
        filename = '{}/worldometers.info/{}/{}.csv'.format(prefix, updated_at[:6], updated_at)
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for i, row in enumerate(data):
                if not i:
                    row = [x.replace(',', '/') for x in row]
                else:
                    row = [x.replace(',', '').replace('+', '') for x in row]
                if 'total' in row[0].lower():
                    continue
                writer.writerow(row)
    filename and shutil.copyfile(filename, '{}/worldometers.info/latest.csv'.format(prefix))
