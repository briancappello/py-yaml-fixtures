# CHANGELOG

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
