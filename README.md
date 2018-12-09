# Py YAML Fixtures

A library for loading database fixtures written in [Jinja2](http://jinja.pocoo.org/)-templated YAML files. It comes with support for [faker](http://faker.readthedocs.io/en/master/) and relationships between fixture objects. Currently it works with the following packages:

- **[Django 2+](https://www.djangoproject.com/)**
- **[Flask SQLAlchemy](http://flask-sqlalchemy.pocoo.org)**
- **[Flask Unchained](https://github.com/briancappello/flask-unchained)**
- Standalone **[SQLAlchemy](https://www.sqlalchemy.org/)**

Requires **Python 3.5+**

## Useful Links

* [Fork it on GitHub](https://github.com/briancappello/py-yaml-fixtures)
* [Documentation](https://py-yaml-fixtures.readthedocs.io/en/latest/)
* [PyPI](https://pypi.org/project/Py-YAML-Fixtures/)

```bash
pip install py-yaml-fixtures
```

## Table of Contents

* [Fixture File Syntax](https://github.com/briancappello/py-yaml-fixtures#fixture-file-syntax)
   * [Relationships](https://github.com/briancappello/py-yaml-fixtures#relationships)
* [Faker and Jinja Templating](https://github.com/briancappello/py-yaml-fixtures#faker-and-jinja-templating)
* [Installation](https://github.com/briancappello/py-yaml-fixtures#installation)
   * [Configuration](https://github.com/briancappello/py-yaml-fixtures#configuration)
      * [With Django](https://github.com/briancappello/py-yaml-fixtures#with-django)
      * [With Flask and Flask-SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-flask-and-flask-sqlalchemy)
      * [With Flask Unchained](https://github.com/briancappello/py-yaml-fixtures#with-flask-unchained)
      * [With Standalone SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-standalone-sqlalchemy)
* [Contributing](https://github.com/briancappello/py-yaml-fixtures#contributing)
   * [Adding support for other ORMs](https://github.com/briancappello/py-yaml-fixtures#adding-support-for-other-orms)
* [License](https://github.com/briancappello/py-yaml-fixtures#license)

## Fixture File Syntax

Using the `Parent` and `Child` models shown just above as an example, to populate these models with some fixtures data, you must create `.yaml` (or `.yml`) files in `PY_YAML_FIXTURES_DIR` named after each model's class name (`Parent` and `Child` in our case). For example:

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

### Relationships

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

## Faker and Jinja Templating

All of the YAML fixtures files are rendered by Jinja before getting loaded. This means you have full access to the Jinja environment, and can use things like `faker`, `range` and `random`:

```jinja2
# db/fixtures/Child.yaml

{% for i in range(0, 20) %}
child{{ i }}:
  name: {{ faker.name() }}
{% endfor %}
```

```jinja2
# db/fixtures/Parent.yaml

{% for i in range(0, 10) %}
parent{{ i }}:
  name: {{ faker.name() }}
  children: {{ random_models('Child', 0, range(0, 4)|random) }}
{% endfor %}
```

There are also two included Jinja helper functions:

* `random_model(model_name: str)`
   - For example, to get one random `Child` model: `{{ random_model('Child') }}`
* `random_models(model_name: str, min_count: int = 0, max_count: int = 3)`
   - For example, to get a list of 0 to 3 `Child` models: `{{ random_models('Child') }}`
   - For example, to get a list of 1 to 4 `Child` models: `{{ random_models('Child', 1, 4) }}`

## Installation

```bash
# to use with django
pip install py-yaml-fixtures[django]

# to use with flask-sqlalchemy
pip install py-yaml-fixtures[flask-sqlalchemy]

# to use with flask-unchained
pip install py-yaml-fixtures[flask-unchained]

# to use with standalone sqlalchemy
pip install py-yaml-fixtures[sqlalchemy]
```

### Configuration

* [With Django](https://github.com/briancappello/py-yaml-fixtures#with-django)
* [With Flask and Flask-SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-flask-and-flask-sqlalchemy)
* [With Flask Unchained](https://github.com/briancappello/py-yaml-fixtures#with-flask-unchained)
* [With Standalone SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-standalone-sqlalchemy)

#### With [Django](https://www.djangoproject.com/)

Add `py_yaml_fixtures` to your `settings.INSTALLED_APPS`.

The `py_yaml_fixtures` app adds one command: `manage.py import_fixtures`. It looks for fixture files in every app configured in your `settings.INSTALLED_APPS` that has a `fixtures` folder. For example:

```bash
# example folder structure:

# app
project-root/app/fixtures/
project-root/app/fixtures/ModelOne.yaml

# blog
project-root/blog/fixtures/
project-root/blog/fixtures/ModelTwo.yaml

# auth
project-root/auth/fixtures/
project-root/auth/fixtures/ModelThree.yaml
project-root/auth/fixtures/ModelFour.yaml
```

```python
# project-root/your_app/settings.py

INSTALLED_APPS = [
   # ...
   'py_yaml_fixtures',

   'app',
   'blog',
   'auth',
]
```

To load the model fixtures into the database, you would run:

```bash
cd your-django-project-root

# to load fixtures from all apps
./manage.py import_fixtures

# or to load fixtures from specific apps
./manage.py import_fixtures app blog
```

#### With [Flask](http://flask.pocoo.org/) and [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org)

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

#### With [Flask Unchained](https://github.com/briancappello/flask-unchained)

Add `py_yaml_fixtures` to your `unchained_config.BUNDLES`.

The PyYAMLFixtures bundle adds one command to Flask Unchained: `flask db import-fixtures`. It looks for fixture files in each bundle's `fixtures` folder (if it exists). For example:

```bash
# example folder structure:

# app
project-root/app/fixtures/
project-root/app/fixtures/ModelOne.yaml

# blog_bundle
project-root/bundles/blog/
project-root/bundles/blog/Post.yaml

# security_bundle
project-root/bundles/security/
project-root/bundles/security/User.yaml
project-root/bundles/security/Role.yaml
```

```python
# project-root/unchained_config.py

BUNDLES = [
    # ...
    'flask_unchained.bundles.sqlalchemy',
    'py_yaml_fixtures',

    'bundles.security',
    'app',
]
```

To load the model fixtures into the database, you would run:

```bash
cd your-flask-unchained-project-root

# to load fixtures from all bundles
flask db import-fixtures

# or to load fixtures from specific bundles
flask db import-fixtures app security_bundle
```

#### With Standalone [SQLAlchemy](https://www.sqlalchemy.org/)

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

## Contributing

Contributions are welcome!

* Please file bug reports as GitHub issues.
* Or even better, open a pull request with the fix!

### Adding support for other ORMs

You must implement a concrete factory by extending `py_yaml_fixtures.FactoryInterface`. There are three abstract methods that must be implemented: `create_or_update`, `get_relationships`, and `maybe_convert_values` (see the [DjangoModelFactory](https://github.com/briancappello/py-yaml-fixtures/blob/master/py_yaml_fixtures/factories/django.py) and [SQLAlchemyModelFactory](https://github.com/briancappello/py-yaml-fixtures/blob/master/py_yaml_fixtures/factories/sqlalchemy.py) implementations as examples).

## License

MIT
