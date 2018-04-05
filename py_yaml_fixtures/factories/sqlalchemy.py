import datetime as dt

from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.associationproxy import AssociationProxy
from types import FunctionType
from typing import *

from ..types import Identifier
from .. import utils
from ..factory_interface import FactoryInterface


class SQLAlchemyModelFactory(FactoryInterface):
    def __init__(self,
                 session: sa_orm.Session,
                 models: Union[List[type], Dict[str, type]],
                 date_factory: Optional[FunctionType] = None,
                 datetime_factory: Optional[FunctionType] = None):
        """
        :param session: the sqlalchemy session
        :param models: list of model classes, or dictionary of models by name
        :param date_factory: function used to generate dates (takes one
            parameter, the text value to convert)
        :param datetime_factory: function used to generate datetimes (takes one
            parameter, the text value to convert)
        """
        super().__init__()
        self.session = session
        self.models = (models if isinstance(models, dict)
                       else {model.__name__: model for model in models})
        self.model_instances = {}
        self.datetime_factory = datetime_factory or utils.datetime_factory
        self.date_factory = date_factory or utils.date_factory

    def create(self, identifier: Identifier, data: Dict[str, Any]):
        model_class = self.models[identifier.class_name]
        instance = self._get_existing(identifier, data)
        if not instance:
            instance = model_class(**data)
        else:
            for attr, value in data.items():
                setattr(instance, attr, value)

        self.session.add(instance)
        self.model_instances[identifier.key] = instance
        return instance

    def _get_existing(self, identifier: Identifier, data: Dict[str, Any]):
        model_class = self.models[identifier.class_name]
        instance = self.model_instances.get(identifier.key)
        if isinstance(instance, model_class) and instance in self.session:
            return instance

        filter_kwargs = {}
        for col in model_class.__mapper__.columns:
            if col.name in data and (col.primary_key or col.unique):
                filter_kwargs[col.name] = data[col.name]
        if not filter_kwargs:
            filter_kwargs = {k: v for k, v in data.items()
                             if v is None
                             or isinstance(v, (bool, int, str, float))}
        if not filter_kwargs:
            return None

        with self.session.no_autoflush:
            return model_class.query.filter_by(**filter_kwargs).one_or_none()

    def maybe_convert_values(self,
                             identifier: Identifier,
                             data: Dict[str, Any],
                             ) -> Dict[str, Any]:
        model_class = self.models[identifier.class_name]
        rv = data.copy()
        for col_name, value in data.items():
            col = getattr(model_class, col_name)
            if (isinstance(col, AssociationProxy)
                    or (col.impl and col.impl.uses_objects)):
                rv[col_name] = self.loader.convert_identifiers(value)
            elif not hasattr(col, 'type'):
                continue
            elif col.type.python_type == dt.date:
                rv[col_name] = self.date_factory(value)
            elif col.type.python_type == dt.datetime:
                rv[col_name] = self.datetime_factory(value)
        return rv

    def commit(self):
        self.session.commit()
