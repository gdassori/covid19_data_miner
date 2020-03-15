import typing

from covid_data_miner.src.sources.csse_points_service import CSSEGISandDataPointsService
from covid_data_miner.src.sources.dpc_ita_github_points_service import DPCItaGithubPointsService
from covid_data_miner.src.sources.worldometers_github_points_service import WorldometersGithubPointsService


class SourcesFactory:
    def __init__(self):
        self._sources = {
            'worldometers': WorldometersGithubPointsService,
            'csse': CSSEGISandDataPointsService,
            'dpc_ita': DPCItaGithubPointsService
        }

    def get_source(self, source_config: typing.Dict):
        cls = self._sources[source_config['name']]
        return cls(source_config.get('authentication_key', ""))

    def list_sources(self):
        res = []
        keys = sorted(self._sources.keys())
        for key in keys:
            res.append({
                "name": key,
                "tags": self._sources[key].tags
            })
        return res
