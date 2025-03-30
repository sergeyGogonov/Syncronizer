import abc
from io import BufferedReader
from typing import Any, ContextManager, Optional
from domain.shared.readOnlyDict import ReadOnlyDict


class DataInfoBuilder(abc.ABC):
    @abc.abstractmethod
    def build(self, info: 'IdentifiedInfo') -> 'DataInfo':
        ...

class BinaryDataKeeper(abc.ABC):
    @abc.abstractmethod
    def keep(self):
        ...

    @abc.abstractmethod
    def is_keeped(self) -> bool:
        ...

    @property
    @abc.abstractmethod
    def keeped_data(self) -> BufferedReader:
        ...


class BinaryDataKeeperFabric(abc.ABC):
    @abc.abstractmethod
    def build(self) -> BinaryDataKeeper:
        ...


class IdentifiedElement:
    def __init__(self, id: int):
        self._id = id

    @property
    def id(self):
        return self._id


class IdentifiedInfo(IdentifiedElement):
    def __init__(self, id: int, info: dict[str, Any]) -> None:
        self._id = id
        self._info = info
    
    @property
    def info(self):
        return self._info


class DataInfo(IdentifiedElement):
    def __init__(
        self,
        id: int,
        hash: bytes,
        meta_info: dict[str, str],
        b_data_keeper: BinaryDataKeeper
    ):
        super().__init__(id)
        self._hash = hash
        self._meta_info = ReadOnlyDict(meta_info)
        self._b_data_keeper = b_data_keeper 
    
    @property
    def meta_info(self):
        return self._meta_info

    @property
    def hash(self):
        return self._hash

    @property
    def b_data_keeper(self):
        return self._b_data_keeper
    
    def __repr__(self):
        return f'DataInfo(id={self._id}, meta_info={self._meta_info})'


