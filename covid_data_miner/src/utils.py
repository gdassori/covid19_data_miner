def influxdb_repository_factory():
    from covid_data_miner.src.influx_repository import InfluxDataRepository
    from influxdb import InfluxDBClient
    from covid_data_miner.src import settings

    if not influxdb_repository_factory.repo:
        influxdb_repository_factory.repo = InfluxDataRepository(
            InfluxDBClient(host=settings.INFLUXDB_HOST, port=settings.INFLUXDB_PORT)
        )
    return influxdb_repository_factory.repo


influxdb_repository_factory.repo = None


def load_config_file():
    return {
        "github_api_key": "",
        "source": [],
        "projections": [],
        "plugins": [],
    }
