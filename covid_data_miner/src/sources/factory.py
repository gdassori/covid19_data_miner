import typing

from covid_data_miner.src.sources.csse_points_service import CSSEGISandDataPointsService
from covid_data_miner.src.sources.worldometers_github_points_service import WorldometersGithubPointsService


class SourcesFactory:
    def __init__(self, default_github_key):
        self._github_key = default_github_key
        self._sources = {
            'worldometers': WorldometersGithubPointsService,
            'csse': CSSEGISandDataPointsService
        }

    def get_source(self, source_config: typing.Dict):
        assert self._github_key
        cls = self._sources[source_config['name']]
        return cls(
            source_config.get('authentication_key', self._github_key)
        )

    def list_sources(self):
        res = []
        keys = sorted(self._sources.keys())
        for key in keys:
            res.append({
                "name": key,
                "tags": self._sources[key].tags
            })
        return res
