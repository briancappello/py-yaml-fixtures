# CHANGELOG

## v0.6.1 (2020/07/26)

- support filtering for existing models by date/datetime in the SQLAlchemy factory (thanks to @westonplatter)
- fix filtering for existing models on the singular side of a o2m relationship in the SQLAlchemy factory (thanks to @westonplatter)
- add tests for usage with standalone SQLAlchemy
- add integration tests for usage with Flask Unchained
- document known limitations

## v0.6.0 (2020/02/09)

- support Flask Unchained v0.8
- support Faker v3
- let factories support duplicate identifiers across model classes
- add `django.contrib.auth.hashers.make_password` as `hash_password` to jinja env
- add basic integration test for django
- add support for datetime.timedelta to SQLAlchemyModelFactory

## v0.5.0 (2019/09/17)

- fix bugs in `date_factory` and `datetime_factory` functions, add tests
- support loading multiple models from individual files named `fixtures.yml` or `fixtures.yaml`
- fix bugs with loading fixtures using stock SQLAlchemy

## v0.4.0 (2018/12/08)

- add Django support
- add Flask Unchained support
- improve docs

## v0.3.2 (2018/12/08)

- add support for loading fixtures from one or more directories

## v0.3.1 (2018/12/07)

- add back support for optional YAML list syntax when the number of identifiers is two or more

## v0.3.0 (2018/12/07)

- add support for determining the correct order to instantiate models (`py-yaml-fixtures` *should* now work with complex relationships)
- major refactor to simplify the `FixturesLoader` class
- add `random_model` and `random_models` Jinja helper functions

## v0.2.0 (2018/09/26)

- Add support for Flask-SQLAlchemy-Unchained

## v0.1.3 (2018/08/14)

- support multi-line identifier strings
- support empty identifier strings (only a class name without any key)
- add documentation

## v0.1.2 (2018/07/31)

- fix `datetime_factory` and `date_factory` utility functions when passed None

## v0.1.1 (2018/04/06)

- fix release (misconfigured `include_packages` in `setup.py`)

## v0.1.0 (2018/04/06)

- initial release
