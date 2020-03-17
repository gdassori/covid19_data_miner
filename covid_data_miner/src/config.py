import json
import os

from covid_data_miner.src import settings, exceptions


class ConfigurationContext:
    def _init__(self):
        self._config = None
        self._config_file_path = None

    @property
    def github_api_key(self):
        return self._config['default']['github_api_key']

    @property
    def influxdb_host(self):
        return self._config['default']['influxdb_host']

    @property
    def influxdb_port(self):
        return self._config['default']['influxdb_port']

    @property
    def sources(self):
        sources = self._config['sources']
        res = {}
        for name, data in sources.items():
            res[name] = data
            if not data.get('authentication_key', ''):
                res[name]['authentication_key'] = self.github_api_key
        return sources

    @property
    def projections(self):
        return self._config['projections']

    @property
    def plugins(self):
        return self._config['plugins']

    def _load_config_file(self, config_file):
        try:
            with open(config_file, 'r') as f:
                self._config = json.load(f)
                self._config_file_path = config_file
            return True
        except:
            pass
        return False

    def _init_config_file(self, config_file: str):
        try:
            directory, filename = os.path.split(config_file)
            userpath = os.path.expanduser("~")
            if directory == '{}/.covid19'.format(userpath):
                os.makedirs(directory, exist_ok=True)
            self._config_file_path = config_file
        except:
            raise exceptions.InvalidPath
        if not filename or not filename.endswith('.json'):
            raise exceptions.InvalidConfigFileName
        if not os.path.isdir(directory):
            raise exceptions.DirectoryNotExists
        self._config = {
            "default": {
                "influxdb_host": settings.DEFAULT_INFLUXDB_HOST,
                "influxdb_port": settings.DEFAULT_INFLUXDB_PORT,
                "github_api_key": ""
            },
            "sources": {},
            "projections": {},
            "plugins": {}
        }
        return self._save_config_file()

    def _save_config_file(self):
        try:
            with open(self._config_file_path, 'w') as f:
                json.dump(self._config, f, indent=4)
        except:
            raise exceptions.ErrorSavingConfigFile
        return True

    def load_config_file(self, config_file):
        if not self._load_config_file(config_file):
            self._init_config_file(config_file)

    def get_configured_sources(self):
        return self._config['sources']

    def get_configured_source(self, source_name):
        return self._config['sources'].get(source_name)

    def add_source(self, source_name, authentication_key):
        if source_name not in self._config['sources']:
            self._config['sources'][source_name] = {
                "authentication_key": authentication_key or ""
            }
        self._config['sources'][source_name]['enabled'] = True
        return self._save_config_file()

    def enable_source(self, source_name):
        self._config['sources'][source_name]['enabled'] = True
        return self._save_config_file()

    def disable_source(self, source_name):
        assert source_name in self._config['sources']
        self._config['sources'][source_name]['enabled'] = False
        return self._save_config_file()

    def remove_source(self, source_name):
        self._config['sources'].pop(source_name)
        return self._save_config_file()

    def get_configured_projections(self):
        return self._config['projections']

    def get_configured_projection(self, projection_name):
        return self._config['projections'].get(projection_name)

    def add_projection(self, projection_name, source, tag, timeframe, alias):
        if projection_name not in self._config['projections']:
            self._config['projections'][alias] = {
                "type": projection_name,
                "source": source,
                "tag": tag,
                "timeframe": timeframe
            }
        self._config['projections'][alias]['enabled'] = True
        return self._save_config_file()

    def enable_projection(self, alias):
        self._config['projections'][alias]['enabled'] = True
        return self._save_config_file()

    def disable_projection(self, alias):
        assert alias in self._config['projections']
        self._config['projections'][alias]['enabled'] = False
        return self._save_config_file()

    def remove_projection(self, projection_name):
        self._config['projections'].pop(projection_name)
        return self._save_config_file()

    def set_github_api_key(self, api_key):
        self._config['default']['github_api_key'] = api_key
        return self._save_config_file()

    def set_influxdb_endpoint(self, host, port):
        self._config['default']['influxdb_host'] = host
        self._config['default']['influxdb_port'] = port
        return self._save_config_file()
