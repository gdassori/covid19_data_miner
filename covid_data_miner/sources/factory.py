import typing

from covid_data_miner.sources.csse_points_service import CSSEGISandDataPointsService
from covid_data_miner.sources.worldometers_github_points_service import WorldometersGithubPointsService


class SourcesFactory:
    def __init__(self, default_github_key):
        self._github_key = default_github_key
        self._sources = {
            'worldometers': WorldometersGithubPointsService,
            'csse': CSSEGISandDataPointsService,
            'protezione_civile_ita': NotImplementedError
        }

    def get_source(self, source_config: typing.Dict):
        cls = self._sources[source_config['name']]
        return cls(
            source_config.get('authentication_key', self._github_key)
        )

    def is_source_valid(self, source_name: str):
        assert source_name in self._sources, self._sources.keys()
