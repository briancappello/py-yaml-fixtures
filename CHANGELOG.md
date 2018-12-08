# CHANGELOG

# 0.3.0 (2018/12/07)

* Add support for determining the correct order to instantiate models (`py-yaml-fixtures` should now work with at least semi-complex relationships)
* Major refactor to simplify the `FixturesLoader` class
* Add `random_model` and `random_models` Jinja helper functions

# 0.2.0 (2018/09/26)

* Add support for Flask-SQLAlchemy-Unchained

# 0.1.3 (2018/08/14)

* Support multi-line identifier strings
* Support empty identifier strings (only a class name without any key)
* Add documentation

# 0.1.2 (2018/07/31)

* fix `datetime_factory` and `date_factory` utility functions when passed None

## 0.1.1 (2018/04/06)

* fix release (misconfigured `include_packages` in `setup.py`)

## 0.1.0 (2018/04/06)

* initial release
