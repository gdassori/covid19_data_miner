from covid_data_miner.src.projections.historical_data_summary_projection import HistoricalDataSummaryProjection


class ProjectionsFactory:
    def __init__(self):
        self._projections = {
            'summary': HistoricalDataSummaryProjection
        }

    def get_projection(self, projection_config):
        cls = self._projections[projection_config['type']]
        instance = cls(
            projection_config['source'],
            key=projection_config['tag'],
            projection_name=projection_config['name'],
            interval=projection_config.get('timeframe')
        )
        return instance

    def list_projections(self):
        res = []
        keys = sorted(self._projections.keys())
        for key in keys:
            res.append({
                "name": key,
                "description": self._projections[key].description
            })
        return res
