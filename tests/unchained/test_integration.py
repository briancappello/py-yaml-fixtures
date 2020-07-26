from py_yaml_fixtures.commands import import_fixtures


def test_flask_unchained_integration(cli_runner):
    from unchained_test_app.models import Parent, Child

    r = cli_runner.invoke(import_fixtures, catch_exceptions=False)
    assert r.exit_code == 0, r.output

    parents = Parent.query.all()
    assert len(parents) == 2

    alice = Parent.query.filter_by(name='Alice').one()
    bob = Parent.query.filter_by(name='Bob').one()
    assert parents == [alice, bob]

    children = Child.query.all()
    assert len(children) == 4

    carol = Child.query.filter_by(name='Carol').one()
    eve = Child.query.filter_by(name='Eve').one()
    grace = Child.query.filter_by(name='Grace').one()
    judy = Child.query.filter_by(name='Judy').one()
    assert children == [carol, eve, grace, judy]

    assert len(alice.children) == 2
    assert alice.children == [grace, judy]

    assert len(bob.children) == 2
    assert bob.children == [carol, eve]
