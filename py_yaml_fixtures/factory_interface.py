from typing import *

from .types import Identifier


class FactoryInterface:
    def __init__(self):
        from .fixtures_loader import FixturesLoader
        self.loader: FixturesLoader = None  # set by the FixturesLoader

    def create(self,
               identifier: Identifier,
               data: Dict[str, Any],
               ) -> object:
        raise NotImplementedError

    def maybe_convert_values(self,
                             identifier: Identifier,
                             data: Dict[str, Any],
                             ) -> Dict[str, Any]:
        raise NotImplementedError

    def commit(self):
        pass
