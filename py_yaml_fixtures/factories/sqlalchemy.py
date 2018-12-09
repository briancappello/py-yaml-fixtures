import datetime as dt
import functools

from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.associationproxy import AssociationProxy
from types import FunctionType
from typing import *

from . import FactoryInterface
from .. import utils
from ..types import Identifier


class SQLAlchemyModelFactory(FactoryInterface):
    """
    Concrete factory for the SQLAlchemy ORM.
    """
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

    def create_or_update(self, identifier: Identifier, data: Dict[str, Any]):
        instance = self._get_existing(identifier, data)
        created = False
        if not instance:
            model_class = self.models[identifier.class_name]
            instance = model_class(**data)
            created = True
        else:
            for attr, value in data.items():
                setattr(instance, attr, value)

        self.session.add(instance)
        self.model_instances[identifier.key] = instance
        return instance, created

    def _get_existing(self, identifier: Identifier, data: Dict[str, Any]):
        model_class = self.models[identifier.class_name]
        instance = self.model_instances.get(identifier.key)
        if isinstance(instance, model_class) and instance in self.session:
            return instance

        # try to filter by primary key or any unique columns
        filter_kwargs = {}
        for col in model_class.__mapper__.columns:
            if col.name in data and (col.primary_key or col.unique):
                filter_kwargs[col.name] = data[col.name]

        # otherwise fallback to filtering by simple types
        if not filter_kwargs:
            filter_kwargs = {k: v for k, v in data.items()
                             if v is None
                             or isinstance(v, (bool, int, str, float))}
        if not filter_kwargs:
            return None

        with self.session.no_autoflush:
            return model_class.query.filter_by(**filter_kwargs).one_or_none()

    @functools.lru_cache()
    def get_relationships(self, class_name: str) -> Set[str]:
        rv = set()
        model_class = self.models[class_name]
        for col_name, value in model_class.__mapper__.all_orm_descriptors.items():
            if (isinstance(value, AssociationProxy)
                    or (hasattr(value, 'impl') and value.impl.uses_objects)):
                rv.add(col_name)
        return rv

    def maybe_convert_values(self,
                             identifier: Identifier,
                             data: Dict[str, Any],
                             ) -> Dict[str, Any]:
        model_class = self.models[identifier.class_name]
        relationships = self.get_relationships(identifier.class_name)
        rv = data.copy()
        for col_name, value in data.items():
            col = getattr(model_class, col_name)
            if col_name in relationships:
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
