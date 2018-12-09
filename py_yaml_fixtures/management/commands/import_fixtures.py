import os

from django.apps import apps
from django.core.management.base import BaseCommand

from py_yaml_fixtures import FixturesLoader
from py_yaml_fixtures.factories.django import DjangoModelFactory


class Command(BaseCommand):

    help = 'Import Jinja2-templated YAML database fixtures from apps'

    def add_arguments(self, parser):
        parser.add_argument('apps', nargs='*',
                            help='App names to load from (defaults to all)')

    def handle(self, *args, **options):
        models = []
        fixture_dirs = []

        app_names = options.get('apps')
        app_configs = ([apps.get_app_config(app_name) for app_name in app_names]
                       if app_names else apps.get_app_configs())
        for app_config in app_configs:
            models.extend(app_config.get_models())
            fixtures_dir = os.path.join(app_config.path, 'fixtures')
            if os.path.exists(fixtures_dir):
                fixture_dirs.append((app_config.name, fixtures_dir))

        if not fixture_dirs:
            print('No fixtures found. Exiting.')
            return

        print('Loading fixtures from apps: ' + ', '.join([t[0] for t in fixture_dirs]))
        factory = DjangoModelFactory(models)
        loader = FixturesLoader(factory, fixture_dirs=[t[1] for t in fixture_dirs])
        loader.create_all(lambda identifier, model, created: print(
            '{action} {identifier}: {model}'.format(
                action='Creating' if created else 'Updating',
                identifier=identifier.key,
                model=repr(model)
            )))
        print('Done loading fixtures. Exiting.')
