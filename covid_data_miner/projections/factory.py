from covid_data_miner.projections.historical_data_summary_projection import HistoricalDataSummaryProjection


class ProjectionsFactory:
    def __init__(self, sources_factory):
        self._sources_factory = sources_factory
        self._projections = {
            'summary': HistoricalDataSummaryProjection
        }

    def get_projection(self, projection_config):
        self._sources_factory.is_source_valid(projection_config['source_name'])
        cls = self._projections[projection_config['name']]
        instance = cls(
            projection_config['source_name'],
            key=projection_config['tag'],
            projection_name=projection_config.get('projection_name'),
            interval=projection_config.get('interval')
        )
        return instance
