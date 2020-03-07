from covid_data_miner.src.manager import Covid19DataMinerManager
from covid_data_miner.src.projections.factory import ProjectionsFactory
from covid_data_miner.src.sources.factory import SourcesFactory
from covid_data_miner.src.utils import load_config_file

config = load_config_file()
sources_factory = SourcesFactory(config and config['github_api_key'])
projections_factory = ProjectionsFactory()
plugins_factory = ''
manager = Covid19DataMinerManager(sources_factory, projections_factory, plugins_factory)


