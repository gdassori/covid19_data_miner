docker rm docker-influxdb-grafana
docker run -d \
  --name docker-influxdb-grafana \
  -p 3003:3003 \
  -p 3004:8083 \
  -p 8086:8086 \
  -v /tmp/influxdb:/var/lib/influxdb \
  -v /tmp/grafana:/var/lib/grafana \
  philhawthorne/docker-influxdb-grafana:latest
