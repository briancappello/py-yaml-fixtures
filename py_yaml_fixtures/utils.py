import random
import re

from collections import defaultdict
from datetime import datetime, timezone
from dateutil.parser import parse as parse_datetime
from typing import *

from .types import Identifier


IDENTIFIER_RE = re.compile(r'(?P<class_name>\w+)\((?P<identifiers>[\w,\s]+)\)')


def datetime_factory(value):
    if value in {'today', 'now', 'utcnow'}:
        return datetime.now(timezone.utc)
    elif value not in {None, 'None'}:
        return parse_datetime(value)


def date_factory(value):
    dt = datetime_factory(value)
    if isinstance(dt, datetime):
        return dt.date


def random_model(ctx, model_class_name):
    """
    Get a random model identifier by class name. For example::

        # db/fixtures/Category.yml
        {% for i in range(0, 10) %}
        category{{ i }}:
            name: {{ faker.name() }}
        {% endfor %}

        # db/fixtures/Post.yml
        a_blog_post:
            category: {{ random_model('Category') }}

    Will render to something like the following::

        # db/fixtures/Post.yml (rendered)
        a blog_post:
            category: "Category(category7)"

    :param ctx: The context variables of the current template (passed automatically)
    :param model_class_name: The class name of the model to get.
    """
    model_identifiers = ctx['model_identifiers'][model_class_name]
    if not model_identifiers:
        return 'None'
    idx = random.randrange(0, len(model_identifiers))
    return '"%s(%s)"' % (model_class_name, model_identifiers[idx])


def random_models(ctx, model_class_name, min_count=0, max_count=3):
    """
    Get a random model identifier by class name. Example usage::

        # db/fixtures/Tag.yml
        {% for i in range(0, 10) %}
        tag{{ i }}:
            name: {{ faker.name() }}
        {% endfor %}

        # db/fixtures/Post.yml
        a_blog_post:
            tags: {{ random_models('Tag') }}

    Will render to something like the following::

        # db/fixtures/Post.yml (rendered)
        a blog_post:
            tags: ["Tag(tag2, tag5)"]

    :param ctx: The context variables of the current template (passed automatically)
    :param model_class_name: The class name of the models to get.
    :param min_count: The minimum number of models to return.
    :param max_count: The maximum number of models to return.
    """
    model_identifiers = ctx['model_identifiers'][model_class_name]
    num_models = random.randint(min_count, min(max_count, len(model_identifiers)))
    if num_models == 0:
        return '[]'

    added = set()
    while len(added) < num_models:
        idx = random.randrange(0, len(model_identifiers))
        added.add(model_identifiers[idx])
    return '["%s(%s)"]' % (model_class_name, ','.join(added))

def normalize_identifiers(identifiers: Union[str, List[str]]) -> List[Identifier]:
    if not identifiers:
        return identifiers

    if isinstance(identifiers, str):
        identifiers = _convert_str(identifiers)
    if isinstance(identifiers, (list, tuple)):
        identifiers = _group_by_class_name(identifiers)

    rv = {}
    for class_name, values in identifiers.items():
        if not class_name:
            raise Exception('Identifier must have a class name.')
        for key in _flatten_csv_list(values):
            if not key:
                continue
            rv[key] = Identifier(class_name, key)
    return list(rv.values())


def _group_by_class_name(identifiers: List[str]) -> DefaultDict[str, List[str]]:
    rv = defaultdict(list)
    for v in identifiers:
        if isinstance(v, Identifier):
            rv[v.class_name].append(v.key)
        elif isinstance(v, str):
            for identifier in _convert_str(v):
                rv[identifier.class_name].append(identifier.key)
        else:
            raise Exception(
                'Unexpected type {t} (for {v!r})'.format(t=type(v), v=v))
    return rv


def _flatten_csv_list(identifier_keys: List[str]) -> List[str]:
    return [key.strip()
            for keys in identifier_keys
            for key in keys.strip(',').split(',')]


def _convert_str(value: str) -> List[Identifier]:
    value = ''.join(value.splitlines())
    rv = []
    prev = None
    while True:
        match = IDENTIFIER_RE.search(value, prev.end() if prev else 0)
        if not match and not rv:
            raise Exception('Identifier must have a class name. (got %r)' % value)
        elif not match:
            return rv

        rv.append(Identifier(match.group('class_name'),
                             match.group('identifiers')))
        prev = match
