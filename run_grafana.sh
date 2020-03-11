docker rm docker-influxdb-grafana
mkdir ~/.covid19
docker run -d \
  --name docker-influxdb-grafana \
  -e GF_AUTH_ANONYMOUS_ENABLED=true \
  -p 3003:3003 \
  -p 3004:8083 \
  -p 8086:8086 \
  -v ~/.covid19/influxdb:/var/lib/influxdb \
  -v ~/.covid19/grafana:/var/lib/grafana \
  gdassori/docker-influxdb-grafana:latest
