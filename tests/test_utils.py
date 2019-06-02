import datetime as dt

from py_yaml_fixtures.types import Identifier
from py_yaml_fixtures.utils import date_factory, datetime_factory, normalize_identifiers


def test_date_factory():
    assert date_factory(None) is None
    assert date_factory('') is None
    assert date_factory('None') is None

    today = dt.date.today()
    assert date_factory(today) == today

    datetime = dt.datetime.now()
    assert date_factory(datetime) == datetime.date()

    for shortcut in ['today', 'now', 'utcnow']:
        assert date_factory(shortcut) - dt.date.today() < dt.timedelta(seconds=1)


def test_datetime_factory():
    assert datetime_factory(None) is None
    assert datetime_factory('') is None
    assert datetime_factory('None') is None

    today = dt.date.today()
    assert datetime_factory(today) == dt.datetime.combine(today, dt.time(tzinfo=dt.timezone.utc))

    datetime = dt.datetime.now()
    assert datetime_factory(datetime) == datetime

    for shortcut in ['today', 'now', 'utcnow']:
        assert datetime_factory(shortcut) - dt.datetime.now(dt.timezone.utc) < dt.timedelta(seconds=1)


def test_normalize_identifiers():
    assert normalize_identifiers(None) is None
    assert normalize_identifiers([]) == []

    assert normalize_identifiers('Model(id)') == [Identifier('Model', 'id')]
    assert normalize_identifiers('"Model(id)"') == [Identifier('Model', 'id')]

    assert normalize_identifiers('Model(id1), Model(id2)') == \
           [Identifier('Model', 'id1'), Identifier('Model', 'id2')]
    assert normalize_identifiers('"Model(id1)", "Model(id2)"') == \
           [Identifier('Model', 'id1'), Identifier('Model', 'id2')]
    assert normalize_identifiers('["Model(id1)", "Model(id2)"]') == \
           [Identifier('Model', 'id1'), Identifier('Model', 'id2')]

    assert normalize_identifiers('Model(id1, id2)') == \
           [Identifier('Model', 'id1'), Identifier('Model', 'id2')]
    assert normalize_identifiers('"Model(id1, id2)"') == \
           [Identifier('Model', 'id1'), Identifier('Model', 'id2')]
    assert normalize_identifiers('["Model(id1, id2)"]') == \
           [Identifier('Model', 'id1'), Identifier('Model', 'id2')]

    assert normalize_identifiers(
        '''
        Model(
            id1,
            id2,
        )
        '''
    ) == [Identifier('Model', 'id1'), Identifier('Model', 'id2')]

    assert normalize_identifiers(
        '''
        [
            Model(
                id1,
                id2,
            ),
        ]
        '''
    ) == [Identifier('Model', 'id1'), Identifier('Model', 'id2')]
