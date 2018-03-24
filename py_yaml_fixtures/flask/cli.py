import click
import importlib
import inspect
import os

from flask import current_app as app
from flask.cli import with_appcontext
from flask_sqlalchemy import Model
from ..fixtures_loader import FixturesLoader
from ..factories import SQLAlchemyModelFactory


@click.command()
@with_appcontext
def import_fixtures():
    models_module_name = app.config.get('PY_YAML_FIXTURES_MODELS_MODULE')
    try:
        models_module = importlib.import_module(models_module_name)
    except (ImportError, ModuleNotFoundError) as e:
        e.msg = (e.msg + '. Please make sure the PY_YAML_FIXTURES_MODELS_MODULE'
                         ' is set correctly.')
        raise e

    fixtures_dir = app.config.get('PY_YAML_FIXTURES_DIR')
    if not fixtures_dir or not os.path.exists(fixtures_dir):
        msg = ('Could not find the %r directory, please make sure '
               'PY_YAML_FIXTURES_DIR is set correctly' % fixtures_dir)
        raise NotADirectoryError(msg)

    model_classes = dict(inspect.getmembers(
        models_module,
        lambda obj: inspect.isclass(obj) and issubclass(obj, Model)))

    factory = SQLAlchemyModelFactory(app.extensions['sqlalchemy'].db.session,
                                     model_classes)
    loader = FixturesLoader(factory, fixtures_dir=fixtures_dir)

    click.echo('Loading fixtures from %r for models in %r' % (
        fixtures_dir, models_module_name))
    for identifier_key, model in loader.create_all().items():
        click.echo('Created %s: %r' % (identifier_key, model))
    click.echo('Done adding fixtures')
