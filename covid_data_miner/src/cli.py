import os

import click
from tabulate import tabulate

from covid_data_miner.src import exceptions
from covid_data_miner.src.config import ConfigurationContext
from covid_data_miner.src.main import sources_factory, projections_factory, manager
from covid_data_miner.src.utils import influxdb_repository_factory

context = ConfigurationContext()
userpath = os.path.expanduser("~")


def validate_projection_timeframe(timeframe):
    timeframe = timeframe.lower()
    if timeframe.endswith('d'):
        timeframe = int(timeframe.replace('d', '')) * 86400
    elif timeframe.endswith('h'):
        timeframe = int(timeframe.replace('h', '')) * 3600
    elif timeframe.isnumeric() and not int(timeframe) % 3600:
        timeframe = int(timeframe)
    else:
        click.echo('invalid timeframe "{}"'.format(timeframe))
        click.echo('timeframe must be days (i.e.: 1d), hours (i.e. 12h) or 3600-multiple integer (i.e. 7200)')
        exit(1)
    return timeframe


def validate_projection_alias(alias):
    if not alias:
        return alias
    rules = []
    if len(alias) >= 3 or len(alias) <= 24:
        rules.append(True)
    for ch in alias:
        rules.append(ch.isalpha() or ch.isdigit() or ch in ('_', '-'))
    if not all(rules):
        click.echo('invalid projection alias "{}", len must be 3~24, alpha, numbers, _ or -'.format(
            alias
        ))
        exit(1)
    return alias


@click.group(name='covid19')
@click.option('--conf', '-c', default='{}/.covid19/config.json'.format(userpath))
def main(conf):
    context.load_config_file(conf)


@main.group()
def sources():
    pass


@main.group()
def plugins():
    pass


@main.group()
def settings():
    pass


@main.group()
def projections():
    pass


@main.group()
def update():
    try:
        manager.load_config(context)
    except exceptions.UnknownSourceException as e:
        click.echo('Error: %s' % e)


@main.group()
def rewind():
    try:
        manager.load_config(context)
    except exceptions.UnknownSourceException as e:
        click.echo('Error: %s' % e)


@sources.command()
def ls():
    click.echo('\nAvailable sources:')
    sources = sources_factory.list_sources()
    table = [
        [s['name'], ', '.join(s['tags']), s['country'], s['type'], s['alias']] for s in sources
    ]
    click.echo('\n' + tabulate(table, headers=["name", "tags", "country", "type", "description"]) + '\n')


@sources.command()
def show():
    click.echo('\nShow sources:')
    configured = context.get_configured_sources()
    table = [
        [
            name,
            'on' if value['enabled'] else 'off',
            '-'
        ] for name, value in configured.items()
    ]
    click.echo('\n' + tabulate(table, headers=["name", "status", "last update"]) + '\n')


@sources.command()
@click.argument('name')
@click.option('--auth')
def add(name, auth=None):
    sources = sources_factory.list_sources()
    names = [s['name'] for s in sources]
    if name not in names:
        click.echo('source "{}" does not exist'.format(name))
        exit(1)
    configured = context.get_configured_source(name)
    if configured and configured['enabled']:
        click.echo('source "{}" already added'.format(name))
        exit(1)
    context.add_source(name, auth)
    configured = context.get_configured_source(name)
    source = sources_factory.get_source(configured)
    click.echo('source "{}" added'.format(name))
    click.echo('Adding default projection for first tag')
    tag = source.tags[0]
    timeframe = 86400
    alias = 'summary_{}_{}_{}'.format(name, tag, timeframe)
    context.add_projection('summary', name, tag, timeframe, alias)
    click.echo('summary projection "{}" added'.format(alias))


@sources.command()
@click.argument('name')
def enable(name):
    configured = context.get_configured_source(name)
    if configured and configured['enabled']:
        click.echo('source "{}" already enabled'.format(name))
        exit(1)
    if not configured:
        click.echo('source "{}" not added for sampling'.format(name))
        exit(1)
    context.enable_source(name)
    click.echo('source "{}" enabled'.format(name))


@sources.command()
@click.argument('name')
def disable(name):
    configured = context.get_configured_sources()
    if name not in configured:
        click.echo('source "{}" not added'.format(name))
        exit(1)
    elif not configured[name]['enabled']:
        click.echo('source "{}" already enabled'.format(name))
        exit(1)
    context.disable_source(name)
    click.echo('source "{}" disabled'.format(name))


@sources.command()
@click.argument('name')
def disable(name):
    sources = sources_factory.list_sources()
    names = [s['name'] for s in sources]
    if name not in names:
        click.echo('source "{}" does not exist'.format(name))
        exit(1)
    configured = context.get_configured_sources()
    if name not in configured or not configured[name]['enabled']:
        click.echo('source "{}" not enabled'.format(name))
        exit(1)
    context.disable_source(name)
    click.echo('source "{}" sampling and triggers disabled'.format(name))


@sources.command()
@click.argument('name')
def remove(name):
    sources = sources_factory.list_sources()
    names = [s['name'] for s in sources]
    if name not in names:
        click.echo('source "{}" does not exist'.format(name))
        exit(1)
    configured = context.get_configured_sources()
    if name not in configured:
        click.echo('source "{}" not configured'.format(name))
        exit(1)
    response = input('Remove configured source and source data from db? (y/n) ')
    if response.strip().lower() == 'y':
        influxdb = influxdb_repository_factory()
        influxdb.delete_points_for_source(name)
        context.remove_source(name)
        click.echo('source "{}" removed'.format(name))


@projections.command()
def ls():
    click.echo('\nAvailable projections:')
    projections = projections_factory.list_projections()
    table = [
        [projection['name'], projection['description']] for projection in projections
    ]
    click.echo('\n' + tabulate(table, headers=["name", "description"]) + '\n')


@projections.command()
def show():
    click.echo('\nShow projections:')
    configured = context.get_configured_projections()
    table = [
        [
            name,
            value['type'],
            value['source'],
            value['tag'],
            value['timeframe'],
            'on' if value['enabled'] else 'off',
            '-'
        ] for name, value in configured.items()
    ]
    click.echo('\n' + tabulate(
        table,
        headers=["alias", "type", "source", "tag", "timeframe", "status", "last update"]
    ) + '\n')


@projections.command()
@click.argument('name')
@click.argument('source')
@click.argument('tag')
@click.argument('timeframe')
@click.option('--alias')
def add(name, source, tag, timeframe, alias=None):
    projections = projections_factory.list_projections()
    if name not in [p['name'] for p in projections]:
        click.echo('projection type "{}" does not exists'.format(name))
        exit(1)
    sources = sources_factory.list_sources()
    if source not in [s['name'] for s in sources]:
        click.echo('source "{}" does not exists'.format(source))
        exit(1)
    if tag not in {s['name']: s for s in sources}[source]["tags"]:
        click.echo('invalid tag "{}" for source "{}"'.format(tag, source))
        exit(1)
    configured = context.get_configured_projections()
    timeframe = validate_projection_timeframe(timeframe)
    alias = validate_projection_alias(alias) or 'summary_{}_{}_{}'.format(source, tag, timeframe)
    if alias in configured.keys():
        click.echo('projection alias "{}" already exists'.format(alias))
        exit(1)
    context.add_projection(name, source, tag, timeframe, alias)
    click.echo('projection "{}" added, type "{}"'.format(alias, name))


@projections.command()
@click.argument('alias')
def enable(alias):
    configured = context.get_configured_projections()
    if alias not in configured:
        click.echo('projection "{}" not added'.format(alias))
        exit(1)
    elif configured[alias]['enabled']:
        click.echo('projection "{}" already enabled'.format(alias))
        exit(1)
    context.enable_projection(alias)
    click.echo('projection "{}" enabled'.format(alias))


@projections.command()
@click.argument('alias')
def disable(alias):
    configured = context.get_configured_projections()
    if alias not in configured or not configured[alias]['enabled']:
        click.echo('projection "{}" not enabled'.format(alias))
        exit(1)
    context.disable_projection(alias)
    click.echo('projection "{}" disabled'.format(alias))


@projections.command()
@click.argument('alias')
def remove(alias):
    configured = context.get_configured_projections()
    if alias not in configured:
        click.echo('projection "{}" not configured'.format(alias))
        exit(1)
    response = input('Remove projection and data from db? (y/n) ')
    if response.strip().lower() == 'y':
        from covid_data_miner.src import influx_repository
        #influx_repository.remove_projection(name)
        context.remove_projection(alias)
        click.echo('projection "{}" removed'.format(alias))


@settings.command()
@click.argument('github_api_key')
def set_github_api_key(github_api_key):
    context.set_github_api_key(github_api_key)
    click.echo('\nGithub API key deleted\n') if not github_api_key else click.echo('\nGithub API key saved\n')


@settings.command()
@click.argument('hostname')
@click.argument('port')
def set_influxdb_endpoint(hostname, port):
    context.set_influxdb_endpoint(hostname, int(port))
    click.echo('\nInfluxdb endpoint set, host: {}, port: {}\n'.format(
        hostname, port
    ))


@update.command('source')
@click.argument('name')
@click.option('--no-cascade')
def update_source(name, no_cascade):
    configured = context.get_configured_sources()
    if name not in configured:
        click.echo('source "{}" not configured'.format(name))
        exit(1)
    response = manager.check_source_updates_available(name)
    if not response['updates_available']:
        click.echo('Local data updated, last update %s' % response['remote_last'])
        exit()
    click.echo('Updates available, local: %s, remote: %s' % (response['local_last'], response['remote_last']))
    response = manager.update_source(name, response['local_last'], no_cascade=no_cascade)
    if response['source_updated']:
        click.echo('Source %s updated' % name)
    for projection in response['projections']:
        click.echo('Projection %s updated' % projection)


@update.command('projection')
@click.argument('name')
@click.option('--no-cascade')
def update_projection(name, no_cascade):
    configured = context.get_configured_projections()


@update.command('all')
@click.option('--no-cascade')
def update_all(no_cascade):
    configured = context.get_configured_sources()
    for name in configured.keys():
        response = manager.check_source_updates_available(name)
        if not response['updates_available']:
            click.echo('Local data updated for %s, last update %s' % (name, response['remote_last']))
            continue
        click.echo('Updates available for %s, local: %s, remote: %s' % (
            name, response['local_last'], response['remote_last'])
        )
        response = manager.update_source(name, response['local_last'], no_cascade=no_cascade)
        if response['source_updated']:
            click.echo('Source %s updated' % name)
        for projection in response['projections']:
            click.echo('Projection %s updated' % projection)


@rewind.command('source')
@click.argument('name')
@click.option('--start-from')
@click.option('--no-cascade')
def rewind_source(name, start_from, no_cascade):
    no_cascade = bool(no_cascade)
    start_from = start_from or 0
    configured = context.get_configured_sources()
    if name not in configured:
        click.echo('source "{}" not configured'.format(name))
        exit(1)
    response = manager.update_source(name, start_from, no_cascade=no_cascade)
    if response['source_updated']:
        click.echo('Source %s updated' % name)
    for projection in response['projections']:
        click.echo('Projection %s updated' % projection)


@rewind.command('projection')
@click.argument('name')
@click.option('--start-from')
@click.option('--no-cascade')
def rewind_projection(name, start_from, no_cascade):
    configured = context.get_configured_projection(name)
    if not configured:
        click.echo('projection "{}" not configured'.format(name))
        exit(1)
    try:
        response = manager.rewind_projection(name, start_from=start_from, no_cascade=no_cascade)
        if not response['rewind']:
            click.echo('Rewind failed for projection "{}"'.format(name))
            exit(1)
        else:
            click.echo('Rewind successful for projection "{}"'.format(name))
            exit()
    except exceptions.NoPointsForSource as e:
        click.echo('Error: %s' % e)
        exit(1)


@rewind.command('all')
def rewind_all(no_cascade):
    configured = context.get_configured_sources()
