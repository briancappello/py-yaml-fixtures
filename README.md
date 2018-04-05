# Py YAML Fixtures

A library for loading (database) fixtures written in Jinja-templated YAML files. Comes with [faker](http://faker.readthedocs.io/en/master/), and supports relationships between fixture objects.

## Currently Supported Factories

* SQLAlchemyModelFactory

## Usage

This a generic library, so you can use it however you want, but the intended use case is to add a CLI command to your project for seeding your database. It could also be useful for creating test fixtures, if you're looking for a different solution than [factory_boy](https://factoryboy.readthedocs.io/en/latest/). 

### With Flask and Flask-SQLAlchemy

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from py_yaml_fixtures.flask import PyYAMLFixtures

app = Flask(__name__)
db = SQLAlchemy(app)

# optional configuration settings (these are all the defaults):
app.config['PY_YAML_FIXTURES_MODELS_MODULE'] = 'app.models'
app.config['PY_YAML_FIXTURES_DIR'] = 'db/fixtures'
app.config['PY_YAML_FIXTURES_COMMAND_NAME'] = 'import_fixtures'

fixtures = PyYAMLFixtures(app)
```

Imagine you have two models:

```python
# app/models.py

class Parent(db.Model):
    name = db.Column(db.String)
    children = db.relationship('Child', back_populates='parent')

class Child(db.Model):
    name = db.Column(db.String)
    parent_id = db.foreign_key('Parent')
    parent = db.relationship('Parent', back_populates='children')
```

To populate these models with some fixtures data, you must create `yaml` files in `PY_YAML_FIXTURES_DIR` named after each model. For example:

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

The keys (`alice`, `bob`, grace`, `judy`) are unique ids used to reference objects in relationships. They must be unique across *all* model fixtures. An identifier consists of two parts: the class name and one or more ids. For singular relationships, the notation is `'ModelName(id)'`. For the many-side of relationships, the notation is the same, just combined with YAML's list syntax:

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
    children: ['Child(alice, bob, grace, judy)']
```

And to actually import the fixtures, call `flask import_fixtures` at the command line.

### Faker and Jinja Templating

All of the YAML fixtures files are rendered by Jinja before getting loaded. This means you have full access to the Jinja environment, and can use things like `faker`, `range` and `random`:

```yaml
# db/fixtures/Child.yaml

{% for i in range(0, 20) %}
child{{ i }}:
  name: {{ faker.name() }}
{% endfor %}
```

```yaml
# db/fixtures/Parent.yaml

{% for i in range(0, 10) %}
{%- set num_children = range(0, 4)|random %}
parent{{ i }}:
  name: {{ faker.name() }}
  children: {% if num_children == 0 %}[]{%- endif %}
    {%- for num in range(0, num_children) %}
    - 'Child(child{{ range(0, 20)|random }})'
    {%- endfor %}
{% endfor %}
```

(Note for the astute readers, any duplicates in child relationships will automatically be removed, so it's safe to use random in this way.)

## Contributing

Contributions are welcome!

### Adding support for other ORMs

You must implement a concrete factory by extending `py_yaml_fixtures.FactoryInterface`. There are two abstract methods that must be implemented: `create` and `maybe_convert_values` (see the SQLAlchemyModelFactory implementation as a reference).

## License

MIT
