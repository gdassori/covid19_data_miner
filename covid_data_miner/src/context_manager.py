import json
import os

from covid_data_miner.src import settings, exceptions


class ContextManager:
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
            if directory == f'{userpath}/.covid19':
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
            "sources": [],
            "projections": [],
            "plugins": []
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

    def save_config_file(self):
        pass

    def get_sources(self):
        pass

    def get_enabled_sources_names(self):
        return []

    def get_projections(self):
        pass

    def get_plugins(self):
        pass

    def enable_source(self, source_name):
        pass

    def disable_source(self, source_name):
        pass

    def set_github_api_key(self, api_key):
        self._config['default']['github_api_key'] = api_key
        return self._save_config_file()

    def set_influxdb_endpoint(self, host, port):
        self._config['default']['influxdb_host'] = host
        self._config['default']['influxdb_port'] = port
        return self._save_config_file()
