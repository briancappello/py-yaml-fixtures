# Py YAML Fixtures

A (*work-in-progress*) library for loading database fixtures written in [Jinja2](http://jinja.pocoo.org/)-templated YAML files. It comes with support for [faker](http://faker.readthedocs.io/en/master/) and relationships between fixture objects. Currently it works with the following packages:

- Django 2+
- Flask SQLAlchemy
- Flask Unchained
- Standalone SQLAlchemy

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
   * [Configuration and Usage](https://github.com/briancappello/py-yaml-fixtures#configuration-and-usage)
      * [With Django](https://github.com/briancappello/py-yaml-fixtures#with-django)
      * [With Flask and Flask-SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-flask-and-flask-sqlalchemy)
      * [With Flask Unchained](https://github.com/briancappello/py-yaml-fixtures#with-flask-unchained)
      * [With Standalone SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-standalone-sqlalchemy)
* [Known Limitations](https://github.com/briancappello/py-yaml-fixtures#known-limitations)
   * [One to Many Relationships](https://github.com/briancappello/py-yaml-fixtures#one-to-many-relationships)
   * [Many to Many Relationships](https://github.com/briancappello/py-yaml-fixtures#many-to-many-relationships)
   * [Association Proxies](https://github.com/briancappello/py-yaml-fixtures#association-proxies)
* [Contributing](https://github.com/briancappello/py-yaml-fixtures#contributing)
   * [Adding support for other ORMs](https://github.com/briancappello/py-yaml-fixtures#adding-support-for-other-orms)
* [License](https://github.com/briancappello/py-yaml-fixtures#license)

## Fixture File Syntax

First, let's define some example models to work with:

```python
class Parent(BaseModel):
    __tablename__ = 'parent'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    children = relationship('Child', back_populates='parent')

class Child(BaseModel):
    __tablename__ = 'child'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = relationship('Parent', back_populates='children')
```

To populate these models with fixtures data, you can either create a single `fixtures.yaml` file in your fixtures directory where the top-level keys are the model class names:

```yaml
# db/fixtures/fixtures.yaml

Child:
    alice:
        name: Alice

    bob:
        name: Bob

    grace:
        name: Grace

    judy:
        name: Judy

Parent:
    parent1:
        name: Parent 1
        children: ['Child(alice)', 'Child(bob)']

    parent2:
        name: Parent 2
        children:
          - 'Child(grace)'
          - 'Child(judy)'
```

Or you can create YAML files named after each model's class name (`Parent` and `Child` in our case). For example:

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
```

### Relationships

The top-level YAML keys (`alice`, `bob`, `grace`, `judy`, `parent1`, `parent2`) are unique ids used to reference objects in relationships. They must be unique across *all* model fixtures.

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

### Configuration and Usage

* [With Django](https://github.com/briancappello/py-yaml-fixtures#with-django)
* [With Flask and Flask-SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-flask-and-flask-sqlalchemy)
* [With Flask Unchained](https://github.com/briancappello/py-yaml-fixtures#with-flask-unchained)
* [With Standalone SQLAlchemy](https://github.com/briancappello/py-yaml-fixtures#with-standalone-sqlalchemy)

#### With Django

Add `py_yaml_fixtures` to your `settings.INSTALLED_APPS`.

```python
# project-root/app/settings.py

INSTALLED_APPS = [
   # ...
   'py_yaml_fixtures',

   'auth',
   'blog',
   'app',
]
```

The `py_yaml_fixtures` app adds one command: `manage.py import_fixtures`. It looks for fixture files in every app configured in your `settings.INSTALLED_APPS` that has a `fixtures` folder. So in this example:

```bash
# app
project-root/app/fixtures/
project-root/app/fixtures/ContactSubmission.yaml

# blog
project-root/blog/fixtures/
project-root/blog/fixtures/Article.yaml

# auth
project-root/auth/fixtures/
project-root/auth/fixtures/User.yaml
project-root/auth/fixtures/Group.yaml
```

To load the model fixtures into the database, you would run:

```bash
cd your-django-project-root

# to load fixtures from all apps
./manage.py import_fixtures

# or to load fixtures from specific apps
./manage.py import_fixtures app blog
```

#### With Flask and Flask-SQLAlchemy

This is the minimal setup required to make a Flask cli command available to import fixtures, by default, `flask import-fixtures`:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from py_yaml_fixtures.flask import PyYAMLFixtures

app = Flask(__name__)
db = SQLAlchemy(app)

# optional configuration settings (these are all the defaults):
app.config['FLASK_MODELS_MODULE'] = 'app.models'  # where all of your model classes are imported
app.config['PY_YAML_FIXTURES_DIR'] = 'db/fixtures'  # where your fixtures file(s) live
app.config['PY_YAML_FIXTURES_COMMAND_NAME'] = 'import-fixtures'  # the name of the CLI command

fixtures = PyYAMLFixtures(app)  # instantiate the PyYAMLFixtures Flask Extension
```

After creating fixture files in the configured `PY_YAML_FIXTURES_DIR`, you would then be able to run `flask import-fixtures` to load the fixtures into the database.

#### With Flask Unchained

Add `py_yaml_fixtures` to your `unchained_config.BUNDLES`.

The PyYAMLFixtures bundle adds one command to Flask Unchained: `flask db import-fixtures`. It looks for fixture files in each bundle's `fixtures` folder (if it exists). For example:

```bash
# example folder structure:

# app
project-root/app/fixtures/
project-root/app/fixtures/ModelOne.yaml

# blog_bundle
project-root/bundles/blog/fixtures/
project-root/bundles/blog/fixtures/Post.yaml

# security_bundle
project-root/bundles/security/fixtures/
project-root/bundles/security/fixtures/User.yaml
project-root/bundles/security/fixtures/Role.yaml
```

```python
# project-root/unchained_config.py

BUNDLES = [
    # ...
    'flask_unchained.bundles.sqlalchemy',
    'py_yaml_fixtures',

    'bundles.blog',
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

#### With Standalone SQLAlchemy

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
    __tablename__ = 'parent'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    children = relationship('Child', back_populates='parent')

class Child(BaseModel):
    __tablename__ = 'child'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = relationship('Parent', back_populates='children')

# first we need a list of our model classes to provide to the factory
model_classes = [Parent, Child]

# and we need a session connected to the database, also for the factory
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

# then we create the factory, and pass it to the fixtures loader
factory = SQLAlchemyModelFactory(session, model_classes)
loader = FixturesLoader(factory, fixture_dirs=[PY_YAML_FIXTURES_DIR])

# to create all the fixtures in the database, we have to call loader.create_all()
if __name__ == '__main__':
    # create the tables in the database
    BaseModel.metadata.create_all(bind=engine)

    # and use the loader to import the fixtures data into the database
    loader.create_all(lambda identifier, model, created: print(
        '{action} {identifier}: {model}'.format(
            action='Creating' if created else 'Updating',
            identifier=identifier.key,
            model=repr(model)
        )))
```

## Known Limitations

### One to Many Relationships

It is not possible to "mix" declarations on both sides of a relationship, eg this doesn't work:

```yaml
Parent:
  alice:
    name: Alice
    children:
      - Child(grace)

  bob:
    name: Bob

Child:
  grace:
    name: Grace

  judy:
    name: Judy
    parent: Parent(bob)
```

The above example will raise a circular dependency exception. You can either declare all children on `Parent` models, *or* declare all parents on `Child` models, **but not both**.

### Many to Many Relationships

Let's say we have a many-to-many relationship between the `Article` and `Tag` models:

```python
class ArticleTag(db.Model):
    """Join table between Article and Tag"""
    article_id = db.foreign_key('Article', primary_key=True)
    article = db.relationship('Article', back_populates='article_tags')

    tag_id = db.foreign_key('Tag', primary_key=True)
    tag = db.relationship('Tag', back_populates='tag_articles')

class Article(db.Model):
    title = db.Column(db.String)

    article_tags = db.relationship('ArticleTag', back_populates='article')
    tags = db.association_proxy('article_tags', 'tag')

class Tag(db.Model):
    name = db.Column(db.String)

    tag_articles = db.relationship('ArticleTag', back_populates='tag')
    articles = db.association_proxy('tag_articles', 'article')
```

The relationships must be specified on the join table model `ArticleTag`:

```yaml
Article:
  hello_world:
    title: Hello World

  metaprogramming:
    title: Metaprogramming

Tag:
  coding:
    name: Coding

  beginner:
    name: Beginner

  advanced:
    name: Advanced

ArticleTag:
  at1:
    article: Article(hello_world)
    tag: Tag(coding)
  at2:
    article: Article(hello_world)
    tag: Tag(beginner)

  at3:
    article: Article(metaprogramming)
    tag: Tag(coding)
  at4:
    article: Article(metaprogramming)
    tag: Tag(advanced)
```

### Association Proxies

As of this writing, specifying values directly on association proxy columns is *not* supported.

## Contributing

Contributions are welcome!

* Please file bug reports as GitHub issues.
* Or even better, open a pull request with the fix!

### Adding support for other ORMs

You must implement a concrete factory by extending `py_yaml_fixtures.FactoryInterface`. There are three abstract methods that must be implemented: `create_or_update`, `get_relationships`, and `maybe_convert_values` (see the [DjangoModelFactory](https://github.com/briancappello/py-yaml-fixtures/blob/master/py_yaml_fixtures/factories/django.py) and [SQLAlchemyModelFactory](https://github.com/briancappello/py-yaml-fixtures/blob/master/py_yaml_fixtures/factories/sqlalchemy.py) implementations as examples).

## License

MIT
