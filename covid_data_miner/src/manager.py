class Covid19DataMinerManager:
    def __init__(self, sources_factory, projections_factory, plugins_loader):
        self._sources = {}
        self._projections = {}
        self._plugins = {}
        self._sources_factory = sources_factory
        self._projections_factory = projections_factory
        self._plugins_loader = plugins_loader

    def load_config(self, config):
        for source_config in config.sources:
            self.add_source(source_config, self._sources_factory.get_source(source_config))

        for projection_config in config.projections:
            self.add_projection(projection_config, self._projections_factory.get_projection(projection_config))

        for plugin_config in config.plugins:
            self.add_plugin(plugin_config, self._plugins_loader.get_plugin(plugin_config))

    def add_source(self, source_config, source):
        if source_config['name'] in self._sources:
            raise ValueError('SourceDuplicatedException')
        self._sources[source_config['name']] = source

    def add_projection(self, projection_config, projection):
        if not projection_config['source'] in self._sources:
            raise ValueError('UnknownSourceException')
        if not projection_config['tag'] in self._sources[projection_config['source']].tags:
            raise ValueError('UnknownTagForSourceException')
        self._projections[projection_config['source']] = \
            self._projections.get(projection_config['source'], []) + [projection]

    def add_plugin(self, plugin_name, plugin):
        self._plugins[plugin_name] = plugin

    def remove_source(self, source_name):
        pass

    def remove_projection(self, projection_name):
        pass

    def remove_plugin(self, plugin_name):
        pass

    def rewind_source(self, source):
        pass

    def update_source(self, source):
        pass

    def rewind_projection(self, source, projection):
        pass

    def update_projection(self, source, projection):
        pass

