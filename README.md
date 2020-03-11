# covid19_data_miner

- A sampler to run covid19 data into influxdb grafana ready time series.



#####Done:
- sampler
- projections system 
- first projection: summary 

#####Todo:
- more sources
- plugin system 


##Howto 

- install docker
- `./run_grafana.sh`
- prepare and activate >= python 3.6 virtualenv
- `pip install -r requirements.txt`
- `./covid19 --help`

Open your browser on `http://localhost:3003` and import the dashboard under `contrib/`

#####Configuration by example:
```
./covid19 settings --set-github-api-key <github-api-key>
./covid19 settings --set-influxdb-endpoint localhost 8086
./covid19 sources add worldometers
./covid19 projections add summary worldometers country 1d
```

#####Update to last data:
```
./covid19 update sources worldometers
```

Some stuff is saved into `~/.covid19`
```
:~/covid19_data_miner$ ls ~/.covid19
config.json  grafana  influxdb
:~/covid19_data_miner$
```


Run docker influxdb\grafana image:
```
./run_grafana.sh
```
then open browser on `http://localhost:3003`

#####Inside grafana:

Add influxdb source, database `covid19`
Import a dashboard from contrib directory
Navigate data.

#####Contacts:
- https://twitter.com/khs9ne

#####Features request:
- more sources

