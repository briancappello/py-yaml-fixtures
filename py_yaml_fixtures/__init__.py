"""
    py_yaml_fixtures
    ~~~~~~~~~~~~~~~~

    A simple library to load database fixtures from Jinja-templated YAML files

    :copyright: Copyright © 2018 Brian Cappello
    :license: MIT, see LICENSE for more details
"""

__version__ = '0.4.1'


from .factories import FactoryInterface
from .fixtures_loader import FixturesLoader
