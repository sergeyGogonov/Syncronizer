from typing import Type
from domain.entities.dataInfo import DataInfo
from domain.entities.locationIdentifierProtocol import LocationProtocol
from domain.interfaces.tree import Tree


class RelPathLocationIdentifierProtocol(LocationProtocol):
    @classmethod
    def is_compatible_with(
        cls,
        location_id_protocol: 'Type[LocationProtocol]'
    ) -> bool:
        if issubclass(
            location_id_protocol,
            RelPathLocationIdentifierProtocol
        ):
            return True
        
        return False
    
    @classmethod
    def protocol_str_identifier(cls) -> str:
        ...

    def corvert_tree(self, tree: Tree[DataInfo]) -> Tree[DataInfo]:
        ...
