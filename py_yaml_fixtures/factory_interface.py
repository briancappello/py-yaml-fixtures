from typing import *
from .types import Identifier


class FactoryInterface:
    def create(self, identifier: Identifier, data) -> object:
        raise NotImplementedError

    def maybe_convert_values(self, identifier: Identifier,
                             data: Dict[str, Any],
                             ) -> Dict[str, Any]:
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError
