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
        click.echo(f'invalid timeframe "{timeframe}"')
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
        click.echo(f'invalid projection alias "{alias}", len must be 3~24, alpha, numbers, _ or -')
        exit(1)
    return alias


@click.group(name='covid19')
@click.option('--conf', '-c', default=f'{userpath}/.covid19/config.json')
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
        [s['name'], ', '.join(s['tags'])] for s in sources
    ]
    click.echo('\n' + tabulate(table, headers=["name", "tags"]) + '\n')


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
        click.echo(f'source "{name}" does not exist')
        exit(1)
    configured = context.get_configured_source(name)
    if configured and configured['enabled']:
        click.echo(f'source "{name}" already added')
        exit(1)
    context.add_source(name, auth)
    click.echo(f'source "{name}" added')


@sources.command()
@click.argument('name')
def enable(name):
    configured = context.get_configured_source(name)
    if configured and configured['enabled']:
        click.echo(f'source "{name}" already enabled')
        exit(1)
    if not configured:
        click.echo(f'source "{name}" not added for sampling')
        exit(1)
    context.enable_source(name)
    click.echo(f'source "{name}" enabled')


@sources.command()
@click.argument('name')
def disable(name):
    configured = context.get_configured_sources()
    if name not in configured:
        click.echo(f'source "{name}" not added')
        exit(1)
    elif not configured[name]['enabled']:
        click.echo(f'source "{name}" already enabled')
        exit(1)
    context.disable_source(name)
    click.echo(f'source "{name}" disabled')


@sources.command()
@click.argument('name')
def disable(name):
    sources = sources_factory.list_sources()
    names = [s['name'] for s in sources]
    if name not in names:
        click.echo(f'source "{name}" does not exist')
        exit(1)
    configured = context.get_configured_sources()
    if name not in configured or not configured[name]['enabled']:
        click.echo(f'source "{name}" not enabled')
        exit(1)
    context.disable_source(name)
    click.echo(f'source "{name}" sampling and triggers disabled')


@sources.command()
@click.argument('name')
def remove(name):
    sources = sources_factory.list_sources()
    names = [s['name'] for s in sources]
    if name not in names:
        click.echo(f'source "{name}" does not exist')
        exit(1)
    configured = context.get_configured_sources()
    if name not in configured:
        click.echo(f'source "{name}" not configured')
        exit(1)
    response = input('Remove configured source and source data from db? (y/n) ')
    if response.strip().lower() == 'y':
        influxdb = influxdb_repository_factory()
        influxdb.delete_points_for_source(name)
        context.remove_source(name)
        click.echo(f'source "{name}" removed')


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
        click.echo(f'projection type "{name}" does not exists')
        exit(1)
    sources = sources_factory.list_sources()
    if source not in [s['name'] for s in sources]:
        click.echo(f'source "{source}" does not exists')
        exit(1)
    if tag not in {s['name']: s for s in sources}[source]["tags"]:
        click.echo(f'invalid tag "{tag}" for source "{source}"')
        exit(1)
    configured = context.get_configured_projections()
    timeframe = validate_projection_timeframe(timeframe)
    alias = validate_projection_alias(alias) or f'summary_{source}_{tag}_{timeframe}'
    if alias in configured.keys():
        click.echo(f'projection alias "{alias}" already exists')
        exit(1)
    context.add_projection(name, source, tag, timeframe, alias)
    click.echo(f'source "{alias}" added, type "{name}"')


@projections.command()
@click.argument('alias')
def enable(alias):
    configured = context.get_configured_projections()
    if alias not in configured:
        click.echo(f'projection "{alias}" not added')
        exit(1)
    elif configured[alias]['enabled']:
        click.echo(f'projection "{alias}" already enabled')
        exit(1)
    context.enable_projection(alias)
    click.echo(f'projection "{alias}" enabled')


@projections.command()
@click.argument('alias')
def disable(alias):
    configured = context.get_configured_projections()
    if alias not in configured or not configured[alias]['enabled']:
        click.echo(f'projection "{alias}" not enabled')
        exit(1)
    context.disable_projection(alias)
    click.echo(f'projection "{alias}" disabled')


@projections.command()
@click.argument('alias')
def remove(alias):
    configured = context.get_configured_projections()
    if alias not in configured:
        click.echo(f'projection "{alias}" not configured')
        exit(1)
    response = input('Remove projection and data from db? (y/n) ')
    if response.strip().lower() == 'y':
        from covid_data_miner.src import influx_repository
        #influx_repository.remove_projection(name)
        context.remove_projection(alias)
        click.echo(f'projection "{alias}" removed')


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
    click.echo(f'\nInfluxdb endpoint set, host: {hostname}, port: {port}\n')


@update.command('source')
@click.argument('name')
@click.option('--no-cascade')
def update_source(name, no_cascade):
    configured = context.get_configured_sources()
    if name not in configured:
        click.echo(f'source "{name}" not configured')
        exit(1)
    response = manager.check_source_updates_available(name)
    if not response['updates_available']:
        click.echo('Local data updated, last update %s' % response['remote_last'])
        exit()
    click.echo('Updates available, local: %s, remote: %s' % (response['local_last'], response['remote_last']))
    if manager.update_source(name, response['local_last'], no_cascade=no_cascade):
        click.echo('Source %s updated' % name)


@update.command('projection')
@click.argument('name')
@click.option('--no-cascade')
def update_projection(name, no_cascade):
    configured = context.get_configured_projections()


@update.command('all')
@click.option('--no-cascade')
def update_all(no_cascade):
    configured = context.get_configured_sources()


@rewind.command('source')
@click.argument('name')
@click.option('--no-cascade')
def rewind_source(name, no_cascade):
    pass


@rewind.command('projection')
@click.argument('name')
@click.option('--start-from')
@click.option('--no-cascade')
def rewind_projection(name, start_from, no_cascade):
    configured = context.get_configured_projection(name)
    if not configured:
        click.echo(f'projection "{name}" not configured')
        exit(1)
    try:
        response = manager.rewind_projection(name, start_from=start_from, no_cascade=no_cascade)
        if not response['rewind']:
            click.echo('Rewind failed for projection "%s"' % name)
            exit(1)
        else:
            click.echo('Rewind successful for projection "%s"' % name)
            exit()
    except exceptions.NoPointsForSource as e:
        click.echo('Error: %s' % e)
        exit(1)
