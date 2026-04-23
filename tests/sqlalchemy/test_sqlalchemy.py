import os
import random

import sqlalchemy as sa

from jinja2 import Environment
from sqlalchemy import create_engine
try:
    from sqlalchemy.orm import declarative_base
except:
    from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from py_yaml_fixtures import FixturesLoader
from py_yaml_fixtures.factories.sqlalchemy import SQLAlchemyModelFactory


SQLA_TEST_DIR = os.path.abspath(os.path.dirname(__file__))
CREATE_MODELS_FIXTURES_DIR = os.path.join(SQLA_TEST_DIR, 'create')
UPDATE_MODELS_FIXTURES_DIR = os.path.join(SQLA_TEST_DIR, 'update')
RANDOM_NAMES = ['Harry', 'Sally']


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
    description = sa.Column(sa.Text)

    parent_id = sa.Column(sa.Integer, sa.ForeignKey('parent.id'))
    parent = relationship('Parent', back_populates='children')

    node_id = sa.Column(sa.Integer, sa.ForeignKey('node.id'))
    node = relationship('Node', back_populates='children')


class Node(BaseModel):
    """self-referential tree"""
    __tablename__ = 'node'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    root_id = sa.Column(sa.Integer, sa.ForeignKey('node.id'), nullable=True)
    root = relationship('Node', back_populates='branches', remote_side=[id])
    branches = relationship('Node', back_populates='root')

    children = relationship('Child', back_populates='node')


class StandAlone(BaseModel):
    __tablename__ = 'stand_alone'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


engine = create_engine('sqlite:///:memory:')
BaseModel.metadata.create_all(bind=engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

env = Environment()
env.globals['random_name'] = lambda: random.choice(RANDOM_NAMES)

factory = SQLAlchemyModelFactory(
    session,
    models=[
        model for model in locals().values()
        if isinstance(model, type)
        and issubclass(model, BaseModel)
        and model != BaseModel
    ],
)


def test_sqlalchemy_create():
    loader = FixturesLoader(
        factory,
        fixture_dirs=[CREATE_MODELS_FIXTURES_DIR],
    )
    loader.create_all(jinja_context=dict(
        child=dict(name="First Child")
    ))

    parents = session.query(Parent).all()
    assert len(parents) == 1
    parent = session.query(Parent).filter_by(name='First Parent').one()

    children = session.query(Child).all()
    assert len(children) == 1
    child = session.query(Child).filter_by(name='First Child').one()

    assert parent.children == [child]

    nodes = session.query(Node).all()
    assert len(nodes) == 6
    assert child.node.name == "Root"

    assert session.query(Node).filter_by(name="Dangling").one()

    standalone = session.query(StandAlone).all()
    assert len(standalone) == 1


def test_sqlalchemy_update():
    loader = FixturesLoader(
        factory,
        env=env,
        fixture_dirs=[UPDATE_MODELS_FIXTURES_DIR],
    )
    loader.create_all()

    parents = session.query(Parent).all()
    assert len(parents) == 1
    parent = session.query(Parent).filter_by(name='First Parent').one()

    children = session.query(Child).all()
    assert len(children) == 2
    first_child = session.query(Child).filter_by(name='First Child').one()
    second_child = session.get(Child, 2)
    assert second_child.name in RANDOM_NAMES

    assert parent.children == [first_child, second_child]
