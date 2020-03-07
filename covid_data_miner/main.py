from covid_data_miner import settings
from covid_data_miner.manager import Covid19DataMinerManager
from covid_data_miner.projections.factory import ProjectionsFactory
from covid_data_miner.sources.factory import SourcesFactory

config = load_config_file()

sources_factory = SourcesFactory(settings.GITHUB_API_KEY)
projections_factory = ProjectionsFactory(sources_factory)
plugins_factory = ''

manager = Covid19DataMinerManager(
    sources_factory, projections_factory, plugins_factory
)
manager.load_config(config)
