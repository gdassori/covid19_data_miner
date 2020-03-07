from covid_data_miner.src.projections.historical_data_summary_projection import HistoricalDataSummaryProjection


class ProjectionsFactory:
    def __init__(self):
        self._projections = {
            'summary': HistoricalDataSummaryProjection
        }

    def get_projection(self, projection_config):
        cls = self._projections[projection_config['name']]
        instance = cls(
            projection_config['source'],
            key=projection_config['tag'],
            projection_name=projection_config.get('alias'),
            interval=projection_config.get('interval')
        )
        return instance
