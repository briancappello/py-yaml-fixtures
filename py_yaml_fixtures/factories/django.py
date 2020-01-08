from collections import defaultdict
from types import FunctionType
from typing import *

from django.db import models as db

from ..types import Identifier
from .. import utils
from . import FactoryInterface


class DjangoModelFactory(FactoryInterface):
    """
    Concrete factory for the Django ORM.
    """
    def __init__(self,
                 models: Union[List[type], Dict[str, type]],
                 date_factory: Optional[FunctionType] = None,
                 datetime_factory: Optional[FunctionType] = None):
        super().__init__()
        self.models = (models if isinstance(models, dict)
                       else {model.__name__: model for model in models})
        self.model_instances = defaultdict(dict)
        self.datetime_factory = datetime_factory or utils.datetime_factory
        self.date_factory = date_factory or utils.date_factory

        self.relations = {model.__name__: set() for model in self.models.values()}
        for model in self.models.values():
            for rel in (list(model._meta.fields) + list(model._meta.related_objects)):
                if isinstance(rel, db.ManyToManyRel):
                    self.relations[rel.related_model.__name__].add(rel.field.name)
                elif isinstance(rel, (db.ForeignObject, db.ManyToOneRel)):
                    self.relations[rel.model.__name__].add(rel.name)

    def create_or_update(self,
                         identifier: Identifier,
                         data: Dict[str, Any],
                         ):
        if self.model_instances[identifier.class_name].get(identifier.key):
            return self.model_instances[identifier.class_name][identifier.key], False

        kwargs, defaults, m2m = {}, {}, {}
        model_class = self.models[identifier.class_name]
        for k, v in data.items():
            if not hasattr(model_class, k):
                defaults[k] = v
                continue

            field = model_class._meta.get_field(k)

            if isinstance(field, (db.ManyToManyField, db.ManyToManyRel)):
                m2m[k] = v
                continue

            if field.primary_key or field.unique:
                kwargs[k] = v
            else:
                defaults[k] = v

        if not kwargs:
            instance, created = model_class.objects.update_or_create(**defaults)
        else:
            instance, created = model_class.objects.update_or_create(**kwargs,
                                                                     defaults=defaults)

        for k, v in m2m.items():
            for obj in v:
                getattr(instance, k).add(obj)

        self.model_instances[identifier.class_name][identifier.key] = instance
        return instance, created

    def get_relationships(self, class_name: str):
        return self.relations[class_name]

    def maybe_convert_values(self,
                             identifier: Identifier,
                             data: Dict[str, Any],
                             ):
        model_class = self.models[identifier.class_name]
        relationships = self.get_relationships(identifier.class_name)
        rv = data.copy()
        for field_name, value in data.items():
            if field_name in relationships:
                rv[field_name] = self.loader.convert_identifiers(value)
                continue
            field = model_class._meta.get_field(field_name)
            if isinstance(field, db.fields.DateField):
                rv[field_name] = self.date_factory(value)
            elif isinstance(field, db.fields.DateTimeField):
                rv[field_name] = self.datetime_factory(value)
        return rv
