from py_yaml_fixtures.types import Identifier
from py_yaml_fixtures.utils import normalize_identifiers


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
