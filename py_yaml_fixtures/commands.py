# this file adds the `flask db import-fixtures` command for Flask Unchained

from flask_unchained import unchained
from flask_unchained.cli import click, with_appcontext
from flask_unchained.bundles.sqlalchemy import SQLAlchemyUnchained
from flask_unchained.bundles.sqlalchemy.commands import db

from .factories.sqlalchemy import SQLAlchemyModelFactory
from .fixtures_loader import FixturesLoader
from .hooks import ModelFixtureFoldersHook

db_ext: SQLAlchemyUnchained = unchained.get_local_proxy('db')


@db.command(name='import-fixtures')
@click.argument('bundles', nargs=-1,
                help='Bundle names to load from (defaults to all)')
@with_appcontext
def import_fixtures(bundles=None):
    fixture_dirs = []
    for bundle_name in (bundles or unchained.bundles.keys()):
        bundle = unchained.bundles[bundle_name]
        fixtures_dir = ModelFixtureFoldersHook.get_fixtures_dir(bundle)
        if fixtures_dir:
            fixture_dirs.append(fixtures_dir)
            click.echo(f'Loading fixtures from {bundle_name}')

    if not fixture_dirs:
        click.echo('No fixtures directories were found. Exiting')
        import sys
        sys.exit(0)

    factory = SQLAlchemyModelFactory(db_ext.session,
                                     unchained.sqlalchemy_bundle.models)
    loader = FixturesLoader(factory, fixture_dirs=fixture_dirs)
    loader.create_all(lambda identifier, model, created: click.echo(
        f'{"Creating" if created else "Updating"} {identifier.key}: {model!r}'))
    click.echo('Finished adding fixtures')
