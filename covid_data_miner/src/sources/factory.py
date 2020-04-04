import typing

from covid_data_miner.src.sources.covidtracking_points_service import CovidTrackingUSAPointsService
from covid_data_miner.src.sources.csse_points_service import CSSEGISandDataPointsService
from covid_data_miner.src.sources.dpc_ita_github_points_service import DPCItaGithubPointsService
from covid_data_miner.src.sources.istat_mortalita_settimanale_points_service import IstatWeeklyDeathsGithubPointsService
from covid_data_miner.src.sources.rki_de_github_points_service import RkiDeGithubPointsService
from covid_data_miner.src.sources.world_inhabitants import WorldInhabitantsPointsService
from covid_data_miner.src.sources.worldometers_github_points_service import WorldometersGithubPointsService


class SourcesFactory:
    def __init__(self):
        self._sources = {
            'worldometers': WorldometersGithubPointsService,
            'csse': CSSEGISandDataPointsService,
            'dpc_ita': DPCItaGithubPointsService,
            'covidtracking_usa': CovidTrackingUSAPointsService,
            'rki_de': RkiDeGithubPointsService,
            'istat_weekly_death_rate': IstatWeeklyDeathsGithubPointsService,
            'world_inhabitants': WorldInhabitantsPointsService
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
                "tags": self._sources[key].tags,
                "type": self._sources[key].source_type,
                "alias": self._sources[key].source_name,
                "country": self._sources[key].country
            })
        return res
