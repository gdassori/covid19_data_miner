docker rm covid19
mkdir ~/.covid19
docker run -d \
  --name covid19 \
  -e GF_AUTH_ANONYMOUS_ENABLED=true \
  -p 3003:3003 \
  -v ~/.covid19/influxdb:/var/lib/influxdb \
  -v ~/.covid19/grafana:/var/lib/grafana \
  -v ~/.covid19:/root/.covid19 \
  gdassori/covid19:latest
