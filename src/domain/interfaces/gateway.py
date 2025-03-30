import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, ContextManager, Mapping, Optional, Sequence
    from io import BufferedReader
    from domain.entities.contentHashProtocol import ContentHashProtocol
    from domain.entities.contentTransformationProtocol import DataTransformationProtocol
    from domain.entities.dataInfo import DataInfo, IdentifiedInfo
    from domain.entities.locationIdentifierProtocol import LocationProtocol
    from domain.interfaces.tree import ReadOnlyTree

# Гарантия одних id при запуске
class TreeDataGateway(abc.ABC):
    @abc.abstractmethod
    def get_root(self) -> 'IdentifiedInfo':
        ...

    @abc.abstractmethod
    def get_info_by_id(
        self,
        id: int
    ) -> 'IdentifiedInfo':
        ...
    
    @abc.abstractmethod
    def get_childs_info_by_id(
        self, 
        id: int
    ) -> 'Sequence[IdentifiedInfo]':
        ...

    @abc.abstractmethod
    def get_binary_data_by_id(self, id: int) -> 'BufferedReader':
        ...

    @abc.abstractmethod
    def get_hash_protocol(self) -> 'ContentHashProtocol':
        ...
    
    @abc.abstractmethod
    def get_location_protocol(self) -> 'LocationProtocol':
        ...

    @abc.abstractmethod
    def get_data_transformation_protocol(self) -> 'DataTransformationProtocol':
        ...

class ReadableTreeDataGateway(TreeDataGateway):
    ...

class ModifiableTreeDataGateway(TreeDataGateway):
    @abc.abstractmethod
    def delete_by_id(self, id: int):
        ...
    
    @abc.abstractmethod
    def get_id_for_new_elem(self, id: int) -> int:
        ...

    @abc.abstractmethod
    def save_data_by_id(
        self,
        id: int,
        data: 'BufferedReader',
        info: 'Optional[Mapping[str, Any]]' = None
    ) -> bool:
        ...


# Гарантирует, что идентификаторы обоих интерфейсов совпадают
class GatewayFactory(abc.ABC):
    @abc.abstractmethod
    def get_readable_gateway(
        self,
        location_protocol: 'Optional[LocationProtocol]' = None
    ) -> 'ContextManager[ReadableTreeDataGateway]':
        ...

    @abc.abstractmethod
    def get_modifiable_gateway(
        self,
        location_protocol: 'Optional[LocationProtocol]' = None
    ) -> 'ContextManager[ModifiableTreeDataGateway]':
        ... 

class GatewayError(Exception):
    ...

class IdNotFoundError(Exception):
    ...

