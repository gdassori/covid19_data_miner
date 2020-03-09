from covid_data_miner.src import exceptions


class Covid19DataMinerManager:
    def __init__(self, sources_factory, projections_factory, plugins_loader, repository):
        self._sources = {}
        self._projections = {}
        self._plugins = {}
        self._sources_factory = sources_factory
        self._projections_factory = projections_factory
        self._plugins_loader = plugins_loader
        self.repository = repository

    def load_config(self, config):
        for source_config in config.sources:
            self.add_source(source_config, self._sources_factory.get_source(source_config))

        for projection_config in config.projections:
            self.add_projection(projection_config, self._projections_factory.get_projection(projection_config))

        for plugin_config in config.plugins:
            self.add_plugin(plugin_config, self._plugins_loader.get_plugin(plugin_config))

    def add_source(self, source_config, source):
        if source_config['name'] in self._sources:
            raise exceptions.SourceDuplicatedException
        self._sources[source_config['name']] = source

    def add_projection(self, projection_config, projection):
        if not projection_config['source'] in self._sources:
            raise exceptions.UnknownSourceException
        if not projection_config['tag'] in self._sources[projection_config['source']].tags:
            raise exceptions.UnknownTagForSourceException
        self._projections[projection_config['source']] = \
            self._projections.get(projection_config['source'], []) + [projection]

    def add_plugin(self, plugin_name, plugin):
        self._plugins[plugin_name] = plugin

    def rewind_source(self, source, start_time=None):
        points = self._sources[source].get_points_since(start_time)
        self.repository.delete_points_for_source(source, start_time=start_time)
        self.repository.save_historical_points(points)
        for projection in self._projections.get(source, []):
            projection.project(points)

    def update_source(self, source):
        local_last = self.repository.get_last_update_for_source(source)
        remote_last = self._sources[source].get_last_update()
        if not remote_last or not remote_last > local_last:
            return False
        points = self._sources[source].get_points_since(local_last)
        for projection in self._projections.get(source, []):
            projection.project(points)
        return True
