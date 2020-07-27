import os
import sqlalchemy as sa

from py_yaml_fixtures import FixturesLoader
from py_yaml_fixtures.factories.sqlalchemy import SQLAlchemyModelFactory
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

SQLA_TEST_DIR = os.path.abspath(os.path.dirname(__file__))
CREATE_MODELS_FIXTURES_DIR = os.path.join(SQLA_TEST_DIR, 'create')
UPDATE_MODELS_FIXTURES_DIR = os.path.join(SQLA_TEST_DIR, 'update')


BaseModel = declarative_base()


class Parent(BaseModel):
    __tablename__ = 'parent'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    children = relationship('Child', back_populates='parent')


class Child(BaseModel):
    __tablename__ = 'child'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = relationship('Parent', back_populates='children')


engine = create_engine('sqlite:///:memory:')
BaseModel.metadata.create_all(bind=engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

factory = SQLAlchemyModelFactory(session, models=[Parent, Child])


def test_sqlalchemy_create():
    loader = FixturesLoader(factory, fixture_dirs=[CREATE_MODELS_FIXTURES_DIR])
    loader.create_all()

    parents = session.query(Parent).all()
    assert len(parents) == 1
    parent = session.query(Parent).filter_by(name='First Parent').one()

    children = session.query(Child).all()
    assert len(children) == 1
    child = session.query(Child).filter_by(name='First Child').one()

    assert parent.children == [child]


def test_sqlalchemy_update():
    loader = FixturesLoader(factory, fixture_dirs=[UPDATE_MODELS_FIXTURES_DIR])
    loader.create_all()

    parents = session.query(Parent).all()
    assert len(parents) == 1
    parent = session.query(Parent).filter_by(name='First Parent').one()

    children = session.query(Child).all()
    assert len(children) == 2
    first_child = session.query(Child).filter_by(name='First Child').one()
    second_child = session.query(Child).filter_by(name='Second Child').one()

    assert parent.children == [first_child, second_child]
