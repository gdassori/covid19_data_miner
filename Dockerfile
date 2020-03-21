FROM gdassori/docker-influxdb-grafana:latest

RUN apt-get --quiet --quiet update && apt-get --quiet --quiet --no-install-recommends upgrade
RUN apt-get --quiet --quiet --no-install-recommends install gcc g++ python3-setuptools python3-wheel python3-pip curl make

RUN mkdir /app
ENV PATH="/app:${PATH}"

COPY ./requirements.txt /app
RUN pip3 install -r /app/requirements.txt

COPY . /app