# covid19_data_miner

- A sampler to run covid19 data into influxdb grafana ready time series.

demo: http://covid19.chatsubo.it

The client:

![covid19-cli](https://github.com/gdassori/covid19_data_miner/blob/master/docs/images/covid19-cli.png?raw=true "Covid19 cli")

The dashboard

![covid19-grafana](https://github.com/gdassori/covid19_data_miner/blob/master/docs/images/covid19_grafana.png?raw=true "covid19 dashboard")

![covid19-grafana](https://github.com/gdassori/covid19_data_miner/blob/master/docs/images/country_insight.png?raw=true "covid19 dashboard")

Multiple sources selection

![covid19-grafana](https://github.com/gdassori/covid19_data_miner/blob/master/docs/images/data_sources.png?raw=true "covid19 sources")



##### Done:
- sampler
- projections system 
- first projection: summary 
- 5 different data sources (2 globals, Italy, Germany, USA) 

##### Todo:
- more sources (check github Issues and the [new sources howto](https://github.com/gdassori/covid19_data_miner/blob/master/docs/ADD_MORE_SOURCES.md)).
- -->> **plugin system** <<-- 
- auto import default dashboards in grafana.
- auto configure sources in grafana. 

## First run 

- install docker
- checkout git repository
- run `./runcovid.sh`
- `docker exec -ti covid19 bake_grafana` # Only the first time, setup the grafana dashboard.
- `docker exec -ti covid19 covid19 --help`

Open your browser on `http://localhost:3003` and import the dashboard under `contrib/`

##### Configuration by example:
```
docker exec -ti covid19 covid19 settings --set-github-api-key <github-api-key>
docker exec -ti covid19 covid19 settings --set-influxdb-endpoint localhost 8086
docker exec -ti covid19 covid19 sources add worldometers
docker exec -ti covid19 covid19 projections add summary worldometers country 1d
```

##### Update to last data:
```
./covid19 update sources worldometers
```

Some stuff is saved into `~/.covid19`
```
:~/$ ls ~/.covid19
config.json  grafana  influxdb
:~/$
```


Run docker influxdb\grafana image:
```
./runcovid.sh
```
then open browser on `http://localhost:3003`

The default admin account for Grafana is `root/root`, anonymous dashboard browsing is enabled.

##### Inside grafana:

- The latest dashboard should be updated. 
- The sources should be created.

Open an issue if it doesn't work.


#### Series LAG and different timeranges overlap:
To obtain series lag and overlap series with different timeframes, the InfluxDB Timeshift Proxy is used (https://www.npmjs.com/package/influxdb-timeshift-proxy).

![covid19-grafana](https://github.com/gdassori/covid19_data_miner/blob/master/docs/images/series_lag.png?raw=true "covid19 sources")

An example configuration is:

![covid19-grafana](https://github.com/gdassori/covid19_data_miner/blob/master/docs/images/series_lag_config.png?raw=true "covid19 sources")

Check parameters:
- Query: `InfluxDB-Shifted` is the timeshift proxy previously configured.
- alias: `shift_8_days` is the syntax to define a time shift (using aliasing). To know more check influxdb-timeshift-proxy documentation on the link above.



##### Contacts:
- https://twitter.com/khs9ne
