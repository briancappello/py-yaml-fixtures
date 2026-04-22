from collections import defaultdict
from datetime import date, datetime, time, timedelta
from enum import Enum
from functools import lru_cache
from types import FunctionType
from typing import *

from sqlalchemy import UniqueConstraint, orm as sa_orm, text
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
                 tables_to_exclude_from_autoincrement: Optional[List[str]] = None,
                 date_factory: Optional[FunctionType] = None,
                 datetime_factory: Optional[FunctionType] = None):
        """
        :param session: the sqlalchemy session
        :param models: list of model classes, or dictionary of models by name
        :param tables_to_exclude_from_autoincrement: list of table names to exclude from autoincrement
            parameter, the text value to convert)
        :param datetime_factory: function used to generate datetimes (takes one
            parameter, the text value to convert)
        """
        super().__init__()
        self.session = session
        self.models = (models if isinstance(models, dict)
                       else {model.__name__: model for model in models})
        self.tables_to_exclude_from_autoincrement = tables_to_exclude_from_autoincrement or []
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

        # try composite unique constraints from __table_args__
        if not filter_kwargs:
            filter_kwargs = self._get_composite_unique_filter(
                model_class, data, relationships,
            )

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
            except MultipleResultsFound:
                # The filter was ambiguous (e.g. a model with a composite
                # unique constraint where not all columns were available
                # in the fixture data).  Treat as "not found" so a new
                # record is created.
                return None

    @staticmethod
    def _get_composite_unique_filter(
        model_class,
        data: Dict[str, Any],
        relationships: Set[str],
    ) -> Dict[str, Any]:
        """
        Check composite ``UniqueConstraint``s defined in ``__table_args__``
        and return a filter dict if all columns of any constraint are present
        in ``data``.

        This handles models like::

            class Connector(Base):
                __table_args__ = (
                    UniqueConstraint("ocpp_id", "evse_id", name="..."),
                )

        where neither ``ocpp_id`` nor ``evse_id`` is individually unique, but
        together they form a composite unique key.

        Constraint columns that are foreign keys (e.g. ``evse_id``) are
        matched via their corresponding relationship attribute (e.g. ``evse``)
        if the relationship has already been resolved to a model instance.
        """
        table_args = getattr(model_class, '__table_args__', None)
        if not table_args:
            return {}

        if isinstance(table_args, dict):
            # __table_args__ can also be just a dict of kwargs, no constraints
            return {}

        if not isinstance(table_args, tuple):
            return {}

        # Build a mapping of FK column names to their relationship attribute
        # names, e.g. {"evse_id": "evse", "charging_station_id": "charging_station"}
        fk_col_to_rel = {}
        for rel_name in relationships:
            descriptor = getattr(model_class, rel_name, None)
            prop = getattr(descriptor, 'property', None)
            if prop is not None:
                for local_col in prop.local_columns:
                    fk_col_to_rel[local_col.name] = rel_name

        for arg in table_args:
            if not isinstance(arg, UniqueConstraint):
                continue

            constraint_col_names = [col.name for col in arg.columns]
            filter_kwargs = {}
            all_present = True

            for col_name in constraint_col_names:
                if col_name in data:
                    val = data[col_name]
                    if (isinstance(val, (bool, int, str, float))
                            or (col_name in relationships
                                and hasattr(val, '__mapper__'))):
                        filter_kwargs[col_name] = val
                        continue

                # Check if this FK column maps to a resolved relationship
                rel_name = fk_col_to_rel.get(col_name)
                if rel_name and rel_name in data:
                    val = data[rel_name]
                    if hasattr(val, '__mapper__'):
                        filter_kwargs[rel_name] = val
                        continue

                all_present = False
                break

            if all_present and filter_kwargs:
                return filter_kwargs

        return {}

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

                # Check 1: primary key is a single integer column
                primary_keys = inspect(model).primary_key
                if len(primary_keys) != 1 or primary_keys[0].type.python_type != int:
                    continue

                # Check 2: primary key column is auto-incrementing and not joined table inheritance
                pk_column = primary_keys[0]
                if not pk_column.autoincrement or bool(pk_column.foreign_keys):
                    continue

                # Check 3: table is not in the exclude list
                if model.__tablename__ in self.tables_to_exclude_from_autoincrement:
                    continue

                count = self.session.query(model).count() + 1
                table = f'{model.__tablename__}_id_seq'
                self.session.execute(text(
                    f'ALTER SEQUENCE "{current_schema}"."{table}" RESTART WITH {count}'
                ))
            self.session.commit()
