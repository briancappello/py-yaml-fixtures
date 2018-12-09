from typing import *

from ..types import Identifier


class FactoryInterface:
    """
    Abstract base class for ORM factories. Extend this base class to add support
    for a database ORM.
    """
    def __init__(self):
        from ..fixtures_loader import FixturesLoader
        self.loader: FixturesLoader = None  # set by the FixturesLoader

    def create_or_update(self,
                         identifier: Identifier,
                         data: Dict[str, Any],
                         ) -> Tuple[object, bool]:
        """
        Create or update a model.

        :param identifier: An object with :attr:`class_name` and :attr:`key`
                           attributes
        :param data: A dictionary keyed by column name, with values being the
                     converted values to set on the model instance
        :return: A two-tuple of model instance and whether or not it was created.
        """
        raise NotImplementedError

    def get_relationships(self, class_name: str) -> Set[str]:
        """
        Return a list of model attribute names that could have relationships for
        the given model class name.

        :param class_name: The name of the class name to discover relationships for.
        :return: A set of model attribute names.
        """
        raise NotImplementedError

    def maybe_convert_values(self,
                             identifier: Identifier,
                             data: Dict[str, Any],
                             ) -> Dict[str, Any]:
        """
        Takes a dictionary of raw values for a specific identifier, as parsed
        from the YAML file, and depending upon the type of db column the data
        is meant for, decides what to do with the value (eg leave it alone,
        convert a string to a date/time instance, or convert identifiers to
        model instances by calling :meth:`self.loader.convert_identifiers`)

        :param identifier: An object with :attr:`class_name` and :attr:`key`
                           attributes
        :param data: A dictionary keyed by column name, with values being the
                     raw values as parsed from the YAML
        :return: A dictionary keyed by column name, with values being the
                 converted values meant to be set on the model instance
        """
        raise NotImplementedError

    def commit(self):
        """
        If your ORM implements the data mapper pattern instead of active
        record, then you can implement this method to commit the session after
        all the models have been added to it.
        """
        pass
