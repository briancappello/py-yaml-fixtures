from .cli import import_fixtures


class PyYAMLFixtures:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('PY_YAML_FIXTURES_MODELS_MODULE', 'app.models')
        app.config.setdefault('PY_YAML_FIXTURES_DIR', 'db/fixtures')
        command_name = app.config.setdefault('PY_YAML_FIXTURES_COMMAND_NAME',
                                             'import_fixtures')

        if command_name:
            app.cli.add_command(import_fixtures, command_name)
