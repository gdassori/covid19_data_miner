import datetime
import shutil
import csv
import os
from tools.worldometers_web_points_service import WorldometersWebPointsService
import sys
import string

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

    csvs = [w.fetch_current()]
    filename = None
    updates = []
    printable = set(string.printable)
    for updated_at, data in csvs:
        os.makedirs('{}/worldometers.info/{}'.format(prefix, updated_at[:6]), exist_ok=True)
        filename = '{}/worldometers.info/{}/{}.csv'.format(prefix, updated_at[:6], updated_at)
        updated_at and updates.append(
            int(datetime.datetime.strptime(updated_at, '%Y%m%d%H%M%S').strftime('%s'))
        )
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for i, row in enumerate(data):
                if not i:
                    row = [''.join(filter(lambda x: x in printable, x)).replace(',', '/') for x in row]
                else:
                    row = [x.replace(',', '').replace('+', '') for x in row]
                if 'total' in row[0].lower():
                    continue
                writer.writerow(row)
    max_update = max(updates)
    with open('{}/worldometers.info/updated_at'.format(prefix), 'w') as f:
        f.write(str(max_update))
    filename and shutil.copyfile(filename, '{}/worldometers.info/latest.csv'.format(prefix))
