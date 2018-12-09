# this file makes the `py_yaml_fixtures` package a Flask Unchained bundle

from flask_unchained import Bundle


class PyYAMLFixtures(Bundle):
    command_group_names = ['db']
