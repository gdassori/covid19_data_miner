import yaml


def get_influxdb_repository(hostname, port):
    from covid_data_miner.src.influx_repository import InfluxDataRepository
    from influxdb import InfluxDBClient
    if not get_influxdb_repository.repo:
        get_influxdb_repository.repo = InfluxDataRepository(
            InfluxDBClient(host=hostname, port=port)
        )
    return get_influxdb_repository.repo


def influxdb_repository_factory():
    from covid_data_miner.src.cli import context
    return get_influxdb_repository(context.influxdb_host, context.influxdb_port)


get_influxdb_repository.repo = None


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def normalize_data(data: str) -> str:
    if not normalize_data.data:
        normalize_data.transformers = {}
        import os
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open('{}/normalizers.yaml'.format(__location__)) as f:
            normalize_data.data = yaml.load(f, Loader=yaml.FullLoader)
            for k_dest, values in normalize_data.data.items():
                for v in values:
                    normalize_data.transformers[v] = k_dest
    try:
        v = normalize_data.transformers[data]
        return v
    except KeyError:
        return data


normalize_data.data = None
