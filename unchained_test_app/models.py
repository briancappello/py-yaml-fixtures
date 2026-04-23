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


class Left(db.Model):
    class Meta:
        repr = ('id', 'name')

    name = db.Column(db.String)
    joins = db.relationship('Join', back_populates='left')
    rights = db.association_proxy('joins', 'right')


class Right(db.Model):
    class Meta:
        repr = ('id', 'name')

    name = db.Column(db.String)
    joins = db.relationship('Join', back_populates='right')
    lefts = db.association_proxy('joins', 'left')


class Join(db.Model):
    name = db.Column(db.String)

    left_id = db.foreign_key('Left', primary_key=True)
    left = db.relationship('Left', back_populates='joins')

    right_id = db.foreign_key('Right', primary_key=True)
    right = db.relationship('Right', back_populates='joins')
