import datetime
import typing

from covid_data_miner.src import exceptions


class Covid19DataMinerManager:
    def __init__(self, sources_factory, projections_factory, plugins_loader, repository_factory):
        self._sources = {}
        self._projections_by_source = {}
        self._projections_by_name = {}
        self._plugins = {}
        self._sources_factory = sources_factory
        self._projections_factory = projections_factory
        self._plugins_loader = plugins_loader
        self._repository_factory = repository_factory
        self._repository = None

    @property
    def repository(self):
        if not self._repository:
            self._repository = self._repository_factory()
        return self._repository

    def load_config(self, config):
        for source_name, source_config in config.sources.items():
            source_config.update({'name': source_name})
            self.add_source(source_config, self._sources_factory.get_source(source_config))

        for projection_name, projection_config in config.projections.items():
            projection_config.update({'name': projection_name})
            self.add_projection(projection_config, self._projections_factory.get_projection(projection_config))

        for plugin_name, plugin_config in config.plugins.items():
            plugin_config.update({'name': plugin_name})
            self.add_plugin(plugin_config, self._plugins_loader.get_plugin(plugin_config))

    def add_source(self, source_config, source):
        if source_config['name'] in self._sources:
            raise exceptions.SourceDuplicatedException
        self._sources[source_config['name']] = source

    def add_projection(self, projection_config, projection):
        if not projection_config['source'] in self._sources:
            raise exceptions.UnknownSourceException(
                'missing source for projection "%s": %s' % (projection_config['name'], projection_config['source'])
            )
        if not projection_config['tag'] in self._sources[projection_config['source']].tags:
            raise exceptions.UnknownTagForSourceException
        self._projections_by_source[projection_config['source']] = \
            self._projections_by_source.get(projection_config['source'], []) + [projection]
        self._projections_by_name[projection_config['name']] = projection

    def add_plugin(self, plugin_name, plugin):
        self._plugins[plugin_name] = plugin

    def rewind_source(self, source, start_time=None):
        points = self._sources[source].get_points_since(start_time)
        self.repository.delete_points_for_source(source, start_time=start_time)
        self.repository.save_historical_points(points)
        for projection in self._projections_by_source.get(source, []):
            projection.project(points)

    def check_source_updates_available(self, source):
        local_last = self.repository.get_last_update_for_source(source)
        remote_last = self._sources[source].get_last_update()
        return {
            "updates_available": remote_last and (not local_last or remote_last > local_last),
            "local_last": local_last,
            "remote_last": remote_last
        }

    def update_source(self, source, update_from, no_cascade=False):
        points = self._sources[source].get_points_since(update_from)
        self.repository.save_historical_points(*points)
        if no_cascade:
            return True
        for projection in self._projections_by_source.get(source, []):
            projection.project(points)
        return True

    def rewind_projection(self, projection_name: str, start_from: datetime.datetime, no_cascade: bool):
        projection = self._projections_by_name[projection_name]
        response = projection.rewind(since=start_from, disable_plugins=no_cascade)
        return response
