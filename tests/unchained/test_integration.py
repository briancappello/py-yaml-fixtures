from py_yaml_fixtures.commands import import_fixtures


def test_flask_unchained_integration(cli_runner):
    from unchained_test_app.models import Parent, Child, Left, Right, Join

    r = cli_runner.invoke(import_fixtures, catch_exceptions=False)
    assert r.exit_code == 0, r.output

    parents = Parent.query.all()
    assert len(parents) == 4

    alice = Parent.query.filter_by(name='Alice').one()
    bob = Parent.query.filter_by(name='Bob').one()
    joe = Parent.query.filter_by(name="Joe").one()
    emily = Parent.query.filter_by(name="Emily").one()
    assert parents == [alice, bob, joe, emily]

    children = Child.query.all()
    assert len(children) == 6

    carol = Child.query.filter_by(name='Carol').one()
    eve = Child.query.filter_by(name='Eve').one()
    grace = Child.query.filter_by(name='Grace').one()
    judy = Child.query.filter_by(name='Judy').one()
    bill = Child.query.filter_by(name='Bill').one()
    kid_emily = Child.query.filter_by(name='Emily').one()
    assert children == [carol, eve, grace, judy, bill, kid_emily]

    assert len(alice.children) == 2
    assert alice.children == [grace, judy]

    assert len(bob.children) == 2
    assert bob.children == [carol, eve]

    assert len(joe.children) == 1
    assert joe.children == [bill]

    assert len(emily.children) == 1
    assert emily.children == [kid_emily]

    # test m2m models
    lefts = Left.query.all()
    rights = Right.query.all()
    joins = Join.query.all()

    assert len(lefts) == 2
    assert len(rights) == 2
    assert len(joins) == 2

    left_one = Left.query.filter_by(name='Left One').one()
    left_two = Left.query.filter_by(name='Left Two').one()
    right_one = Right.query.filter_by(name='Right One').one()
    right_two = Right.query.filter_by(name='Right Two').one()

    # assert join.left == left
    # assert join.right == right
    #
    # assert left.joins == [join]
    # assert left.rights == [right]
    #
    # assert right.joins == [join]
    # assert right.lefts == [left]
