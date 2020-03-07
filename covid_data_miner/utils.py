def influxdb_repository_factory():
    from covid_data_miner.influx_repository import InfluxDataRepository
    from influxdb import InfluxDBClient
    from covid_data_miner import settings

    if not influxdb_repository_factory.repo:
        influxdb_repository_factory.repo = InfluxDataRepository(
            InfluxDBClient(host=settings.INFLUXDB_HOST, port=settings.INFLUXDB_PORT)
        )
    return influxdb_repository_factory.repo


influxdb_repository_factory.repo = None
