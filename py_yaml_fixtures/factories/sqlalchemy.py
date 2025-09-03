from collections import defaultdict
from datetime import date, datetime, time, timedelta
from enum import Enum
from functools import lru_cache
from types import FunctionType
from typing import *

from sqlalchemy import orm as sa_orm, text
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.associationproxy import AssociationProxy

from ..types import Identifier
from .. import utils
from . import FactoryInterface


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
        self.model_instances = defaultdict(dict)
        self.datetime_factory = datetime_factory or utils.datetime_factory
        self.date_factory = date_factory or utils.date_factory

    def create_or_update(
        self,
        identifier: Identifier,
        data: Dict[str, Any],
    ):
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
        self.model_instances[identifier.class_name][identifier.key] = instance
        return instance, created

    def _get_existing(self, identifier: Identifier, data: Dict[str, Any]):
        model_class = self.models[identifier.class_name]
        relationships = self.get_relationships(identifier.class_name)
        instance = self.model_instances[identifier.class_name].get(identifier.key)
        if isinstance(instance, model_class) and instance in self.session:
            return instance

        # try to filter by primary key or any unique columns
        filter_kwargs = {}
        for col in model_class.__mapper__.columns:
            if col.name in data and (col.primary_key or col.unique):
                filter_kwargs[col.name] = data[col.name]

        # otherwise fallback to filtering by values
        if not filter_kwargs:
            filter_kwargs = {k: v for k, v in data.items()
                             if (k in relationships and hasattr(v, '__mapper__'))
                             or v is None
                             or isinstance(v, (bool, int, str, float))}
        if not filter_kwargs:
            return None

        filter_expressions = []
        for k, v in filter_kwargs.items():
            filter_expressions.append(getattr(model_class, k) == v)

            if k in relationships:
                for pk in v.__mapper__.primary_key:
                    pk_value = getattr(v, pk.name)
                    if pk_value is None:
                        return None

        with self.session.no_autoflush:
            stmt = self.session.query(model_class).filter(*filter_expressions)
            try:
                return stmt.one_or_none()
            except MultipleResultsFound as e:
                raise MultipleResultsFound(str(stmt)) from e

    @lru_cache()
    def get_relationships(self, class_name: str) -> Set[str]:
        rv = set()
        model_class = self.models[class_name]
        for col_name, value in model_class.__mapper__.all_orm_descriptors.items():
            # FIXME: this is apparently needed to make value.impl accessible?
            getattr(value, 'property', None)

            if (isinstance(value, AssociationProxy)
                    or (getattr(value, 'impl', None) is not None
                        and value.impl.uses_objects)):
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
            try:
                col = getattr(model_class, col_name)
            except AttributeError:
                raise AttributeError(f'Could not find column {col_name} on {model_class}')

            if col_name in relationships:
                rv[col_name] = self.loader.convert_identifiers(value)
                continue
            elif not hasattr(col, 'type'):
                continue

            try:
                py_type = col.type.python_type
            except NotImplementedError:
                # compatibility for sqlmodel AutoString
                py_type = col.type.impl.python_type

            if py_type == date:
                rv[col_name] = self.date_factory(value)
            elif py_type == time:
                rv[col_name] = time(*[int(x) for x in value.split(':')])
            elif py_type == datetime:
                rv[col_name] = self.datetime_factory(value)
            elif py_type == timedelta:
                duration, unit = value.split(" ")
                rv[col_name] = timedelta(**{unit: float(duration)})
            elif isinstance(py_type, type) and issubclass(py_type, Enum):
                try:
                    value = py_type[value]
                except KeyError:
                    value = py_type(value)
                rv[col_name] = value
        return rv

    def commit(self):
        # if the fixture files define primary keys on auto-increment columns,
        # this makes sure auto-increment continues to work for future inserts
        self.session.commit()
        if 'postgresql' in self.session.bind.dialect.name:
            current_schema = self.session.bind.get_execution_options().get(
                'schema_translate_map',
                {None: "public"},
            )[None]

            for model in self.models.values():
                if model.__name__ not in self.model_instances:
                    continue

                primary_keys = inspect(model).primary_key
                if len(primary_keys) != 1 or primary_keys[0].type.python_type != int:
                    continue

                count = self.session.query(model).count() + 1
                table = f'{model.__tablename__}_id_seq'
                self.session.execute(text(
                    f'ALTER SEQUENCE "{current_schema}"."{table}" RESTART WITH {count}'
                ))
            self.session.commit()
