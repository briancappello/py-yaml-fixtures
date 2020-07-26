from flask_unchained.bundles.sqlalchemy import db


class Parent(db.Model):
    class Meta:
        repr = ('id', 'name')

    name = db.Column(db.String)

    children = db.relationship('Child', back_populates='parent')


class Child(db.Model):
    class Meta:
        repr = ('id', 'name')

    name = db.Column(db.String)

    parent_id = db.foreign_key('Parent')
    parent = db.relationship('Parent', back_populates='children')
