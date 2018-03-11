# Py YAML Fixtures

A library for loading (database) fixtures written in Jinja-templated YAML files. Comes with faker, and supports relationships between fixture objects.

## Supported Factories

* SQLAlchemyModelFactory

## Usage

This a generic library, so you can use it however you want, but the intended use case is to add a CLI command to your project for seeding your database. It could also be useful for creating test fixtures, if you're looking for a more simple solution than [factory_boy](https://factoryboy.readthedocs.io/en/latest/). 

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

And then to use it, call `flask import_fixtures` at the command line.

It assumes your fixtures are in a folder, containing file names that match the models you want to create:

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
  children: ['Child(moe, larry, curly)']
  # other supported syntaxes, all resulting in the same list:  (generally, it's 
  # safest to quote strings, so the PyYAML parser doesn't get confused)
  # children: 'Child(moe, larry, curly)'
  # children: ['Child(moe, larry)', 'Child(curly)']
  # children: ['Child(moe)', 'Child(larry)', 'Child(curly)']
  # children:
  #   - 'Child(moe)'
  #   - 'Child(larry)'
  #   - 'Child(curly)'

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
