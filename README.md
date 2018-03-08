# Py YAML Fixtures

A library for loading (database) fixtures written in Jinja-templated YAML files. Comes with faker, and supports relationships between fixture objects.

## Supported Factories

* SQLAlchemyModelFactory

## Usage

This a generic library, so you can use it however you want, but the intended use case is to add a CLI command to your project for seeding your database. It could also be useful for creating test fixtures, if you're looking for a more simple solution than [factory_boy](https://factoryboy.readthedocs.io/en/latest/). It assumes your fixtures are in a folder, containing file names that match the models you want to create:

```
$ ls db/fixtures
Child.yaml
Parent.yaml
```

And then in your fixture templates:

```yaml
# db/fixtures/Child.yaml

moe:
  name: Moe

larry:
  name: Larry

curly:
  name: Curly

{% for i in range(0, 20) %}
child{{ i }}:
  name: {{ faker.name() }}
{% endfor %}
```

```yaml
# db/fixtures/Parent.yaml

# the `three-stooges` key is a identifier used to reference particular models
# NOTE: it must be unique across *all* of your model fixture files
three-stooges:
  name: Three Stooges
  children: Child(moe, larry, curly)  # yaml interprets this as a string
  # other supported syntaxes, all resulting in the same list:  (generally, it's 
  # safest to quote strings, so the PyYAML parser doesn't get confused)
  # children: ['Child(moe, larry, curly)']
  # children: ['Child(moe, larry)', 'Child(curly)']
  # children: ['Child(moe)', 'Child(larry)', 'Child(curly)']
  # children:
  #   - Child(moe)
  #   - Child(larry)
  #   - Child(curly)

{% for i in range(0, 10) %}
parent{{ i }}:
  name: {{ faker.name() }}
  {%- set num_kids = range(0, 4)|random %}
  children: {% if num_kids == 0 %}[]{%- endif %}
    {%- for num in range(0, num_kids) %}
    - 'Child(child{{ range(1, 5)|random }})'
    {%- endfor %}
{% endfor %}
```

(Note for the astute readers, the `FixturesLoader` class will remove any duplicates in child relationships, so it's safe to use random in this way.)

Here's an example command for using it with Flask, SQLAlchemy, and click:

```python
import click
import importlib
import inspect

from flask.cli import with_appcontext
from flask_sqlalchemy import Model
from py_yaml_fixtures import FixturesLoader
from py_yaml_fixtures.factories import SQLAlchemyModelFactory

from app.extensions import db

@click.group()
def fixtures():
    """Import database fixtures"""

@fixtures.command('import')
@click.argument('folder', type=click.Path(exists=True), default='db/fixtures')
@with_appcontext
def import_fixtures(folder):
    model_classes = dict(inspect.getmembers(
        importlib.import_module('app.models'),
        lambda obj: inspect.isclass(obj) and issubclass(obj, Model)))
    # or if you prefer less magic, it's a dict of class names to model classes:
    # model_classes = {'Parent': app.models.Parent, 'Child': app.models.Child}
    factory = SQLAlchemyModelFactory(db.session, model_classes)
    loader = FixturesLoader(factory, fixtures_dir=folder)
    created_instances = loader.create_all()
    for identifier_key, model in created_instances.items():
        click.echo('Created {identifier_key}: {model!r}'.format(
            identifier_key=identifier_key, model=model))
    click.echo('Finished importing fixtures')
```
