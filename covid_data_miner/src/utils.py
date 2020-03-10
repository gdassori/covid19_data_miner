

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
