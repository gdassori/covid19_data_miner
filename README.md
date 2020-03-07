# covid19_data_miner
Covid19 data to influxdb



Todo (concept):
```
$ covid19 source add worldometers

- Added source worldometers

  
$ covid19 summary worldometers country 

- Added summary projection country to source worldometers


$ covid19 source add protezione_civile_ita

- Added source protezione_civile_ita


$ covid19 summary protezione_civile_ita region

- Added summary projection region to source protezione_civile_ita


$ covid19 plugin add worldometers country growth 4d

- Added plugin growth 4d to worldometers country


$ covid19 plugin add worldometers country growth 4d

- Added plugin growth 4d to protezione_civile_ita country


$ covid19 plugin rewind growth 4d worldometers

- Rewind plugin output, first point: 2020-01-29, last: current, done.


$ covid19 update worldometers

- Updating source: worldometers
- Updating projection: summary country
- Updating plugin output: growth 4d on country

  
$ covid19 update protezione_civile_ita

- Updating source: protezione_civile_ita
- Updatingsou projection: summary region
- Updating plugin output: growth 4d on region

  
$ covid19 update all

- Updating source: worldometers
- Updating projection: summary country
- Updating plugin output: growth 4d on country

- Updating source: protezione_civile_ita
- Updating projection: summary region
- Updating plugin output: growth 4d on region

```