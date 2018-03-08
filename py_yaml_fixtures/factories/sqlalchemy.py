import sqlalchemy as sa

from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.associationproxy import AssociationProxy
from types import FunctionType
from typing import *

from ..fixtures_loader import FixturesLoader
from ..types import Identifier
from .. import utils
from ..factory_interface import FactoryInterface


class SQLAlchemyModelFactory(FactoryInterface):
    def __init__(self, session: sa_orm.Session,
                 models: Union[List[type], Dict[str, type]],
                 date_factory: FunctionType = None,
                 datetime_factory: FunctionType = None):
        """
        :param session: the sqlalchemy session
        :param models: list of model classes, or dictionary of models by name
        :param date_factory: function used to generate dates (takes one
            parameter, the text value to convert)
        :param datetime_factory: function used to generate datetimes (takes one
            parameter, the text value to convert)
        """
        self.session = session
        self.models = (models if isinstance(models, dict)
                       else {model.__name__: model for model in models})
        self.datetime_factory = datetime_factory or utils.datetime_factory
        self.date_factory = date_factory or utils.date_factory

        self.loader: FixturesLoader = None  # this gets set by the loader itself
        self.model_instances = {}

    def create(self, identifier: Identifier, data):
        model_class = self.models[identifier.class_name]
        instance = self.model_instances.get(identifier.key)
        if isinstance(instance, model_class) and instance in self.session:
            return instance

        instance = model_class(**self.maybe_convert_values(identifier, data))
        self.session.add(instance)
        self.model_instances[identifier.key] = instance
        return instance

    def maybe_convert_values(self, identifier: Identifier, data: dict) -> dict:
        model_class = self.models[identifier.class_name]
        rv = data.copy()
        for col_name, value in data.items():
            col = getattr(model_class, col_name)
            if (isinstance(col, AssociationProxy)
                    or (col.impl and col.impl.uses_objects)):
                rv[col_name] = self.loader.convert_identifiers(value)
            elif not hasattr(col, 'type'):
                continue
            elif isinstance(col.type, sa.Date):
                rv[col_name] = self.date_factory(value)
            elif isinstance(col.type, sa.DateTime):
                rv[col_name] = self.datetime_factory(value)
        return rv

    def commit(self):
        self.session.commit()
