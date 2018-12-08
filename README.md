# Py YAML Fixtures

A library for loading database fixtures written in [Jinja2](http://jinja.pocoo.org/)-templated YAML files. It comes with support for [faker](http://faker.readthedocs.io/en/master/) and relationships between fixture objects.

## Useful Links

* [Fork it on GitHub](https://github.com/briancappello/py-yaml-fixtures)
* [Documentation](https://py-yaml-fixtures.readthedocs.io/en/latest/)

## Installation

```bash
pip install py-yaml-fixtures[sqlalchemy]
```

## Currently Supported Factories

* SQLAlchemyModelFactory (requires SQLAlchemy be installed)

## Usage

This a generic library, so you can use it however you want, but the intended use case is to add a CLI command to your project for seeding your database. It could also perhaps be useful for creating test fixtures, if you're looking for a different solution than [factory_boy](https://factoryboy.readthedocs.io/en/latest/). 

### With Flask and Flask-SQLAlchemy

This is the minimal setup required to make a Flask cli command available to import fixtures, by default, `flask import-fixtures`:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from py_yaml_fixtures.flask import PyYAMLFixtures

app = Flask(__name__)
db = SQLAlchemy(app)

# optional configuration settings (these are all the defaults):
app.config['FLASK_MODELS_MODULE'] = 'app.models'
app.config['PY_YAML_FIXTURES_DIR'] = 'db/fixtures'
app.config['PY_YAML_FIXTURES_COMMAND_NAME'] = 'import-fixtures'

fixtures = PyYAMLFixtures(app)
```

After creating fixture files in the configured `PY_YAML_FIXTURES_DIR`, you would then be able to run `flask import-fixtures` to load the fixtures into the database.

### With Standalone SQLAlchemy

```python
import sqlalchemy as sa

from py_yaml_fixtures import FixturesLoader
from py_yaml_fixtures.factories.sqlalchemy import SQLAlchemyModelFactory
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

PY_YAML_FIXTURES_DIR = 'db/fixtures'

BaseModel = declarative_base()

class Parent(BaseModel):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    children = relationship('Child', back_populates='parent')

class Child(BaseModel):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = relationship('Parent', back_populates='children')

# first we need a list of our model classes to provide to the factory
models = [Parent, Child]

# and we need a session connected to the database, also for the factory
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

# then we create the factory, and pass it to the fixtures loader
factory = SQLAlchemyModelFactory(session, models)
loader = FixturesLoader(factory, fixture_dirs=[PY_YAML_FIXTURES_DIR])

# to create all the fixtures in the database, we have to call loader.create_all()
if __name__ == '__main__':
    loader.create_all(lambda identifier, model, created: print(
        '{action} {identifier}: {model}'.format(
            action='Creating' if created else 'Updating',
            identifier=identifier.key,
            model=repr(model)
        )))
```

### Fixture File Syntax

Using the `Parent` and `Child` models shown just above as an example, to populate these models with some fixtures data, you must create `yaml` files in `PY_YAML_FIXTURES_DIR` named after each model's class name (`Parent` and `Child` in our case). For example:

```yaml
# db/fixtures/Child.yaml

alice:
    name: Alice

bob:
    name: Bob

grace:
    name: Grace

judy:
    name: Judy
```

The top-level YAML keys (`alice`, `bob`, `grace`, `judy`) are unique ids used to reference objects in relationships. They must be unique across *all* model fixtures.

To reference them, we use an *identifier string*. An identifier string consists of two parts: the class name, and one or more ids. For singular relationships the notation is `'ModelClassName(id)'`. For the many-side of relationships, the notation is the same, just combined with YAML's list syntax:

```yaml
# db/fixtures/Parent.yaml

parent1:
  name: Parent 1
  children: ['Child(alice)', 'Child(bob)']

parent2:
  name: Parent 2
  children:
    - 'Child(grace)'
    - 'Child(judy)'

# or in short-hand notation
parent3:
  name: Parent 3
  children: ['Child(alice, bob)']

# technically, as long as there are at least 2 ids in the identifier string,
# then even the YAML list syntax is optional, and you can write stuff like this:
parent4:
  name: Parent 4
  children: Child(alice, bob)

# or spanning multiple lines:
parent5:
  name: Parent 5
  children: >
    Child(
      grace,
      judy,
    )
```

### Faker and Jinja Templating

All of the YAML fixtures files are rendered by Jinja before getting loaded. This means you have full access to the Jinja environment, and can use things like `faker`, `range` and `random`:

```jinja
# db/fixtures/Child.yaml

{% for i in range(0, 20) %}
child{{ i }}:
  name: {{ faker.name() }}
{% endfor %}
```

```jinja
# db/fixtures/Parent.yaml

{% for i in range(0, 10) %}
parent{{ i }}:
  name: {{ faker.name() }}
  children: {{ random_models('Child', 0, range(0, 4)|random) }}
{% endfor %}
```

There are also two included Jinja helper functions:

* `random_model(model_name: str)`
   - get one random `Child` model: `{{ random_model('Child') }}`
* `random_models(model_name: str, min_count: int = 0, max_count: int = 3)`
   - get a list of 0 to 3 `Child` models: `{{ random_models('Child') }}`
   - get a list of 1 to 4 `Child` models: `{{ random_models('Child', 1, 4) }}`

## Contributing

Contributions are welcome!

* Please file bug reports as GitHub issues.
* Or even better, open a pull request with the fix!

### Adding support for other ORMs

You must implement a concrete factory by extending `py_yaml_fixtures.FactoryInterface`. There are two abstract methods that must be implemented: `create_or_update`, `get_relationships`, and `maybe_convert_values` (see the SQLAlchemyModelFactory implementation as a reference).

## License

MIT
