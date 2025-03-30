import abc
from typing import Type

from domain.entities.dataInfo import DataInfo
from domain.interfaces.tree import Tree


class LocationProtocol(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def protocol_str_identifier(cls) -> str:
        ...
    
    @abc.abstractmethod
    def corvert_tree(
        self,
        tree: Tree[DataInfo],
    ) -> Tree[DataInfo]:
        ...
    

class TmpLocationIdentifierProtocol(LocationProtocol):
    ...

class LongStorageIdentifierProtocol(LocationProtocol):
    ...

class LocationProtocolError(Exception):
    ...

class LocationProtocolCannotApplied(Exception):
    ...
