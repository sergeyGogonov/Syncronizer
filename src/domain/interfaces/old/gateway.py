import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entities.contentHashProtocol import ContentHashProtocol, Type
    from domain.entities.contentTransformationProtocol import ContentTransformationProtocol
    from domain.entities.locationIdentifierProtocol import LocationIdentifierProtocol
    from domain.entities.dataInfo import TreeDataInfoWithBinary
    from typing import Sequence

class Gateway(abc.ABC):
    def __init__(
        self,
        location_id_protocol: 'LocationIdentifierProtocol',
        hash_protocol: 'ContentHashProtocol',
        transformation_protocol: 'ContentTransformationProtocol'
    ):
        self._location_id_protocol = location_id_protocol
        self._hash_protocol = hash_protocol
        self._transformation_protocol = transformation_protocol

    @abc.abstractmethod
    def get_root(self) -> 'TreeDataInfoWithBinary':
        ...

    @abc.abstractmethod
    def get_binary_by_id(self, location_id: str) -> bytes:
        ...
    
    @abc.abstractmethod
    def get_content_by_id(
        self, location_id: str
    ) -> 'TreeDataInfoWithBinary':
        ...
    
    @abc.abstractmethod
    def get_internal_content_by_id(
        self, location_id: str
    ) -> 'Sequence[TreeDataInfoWithBinary]':
        ...

    @abc.abstractmethod
    def save_content_by_id(
        self,
        location_id: str,
        d_info: 'TreeDataInfoWithBinary'
    ) -> bool:
        ...
    
    @property
    @abc.abstractmethod
    def hash_protocol(self) -> 'ContentHashProtocol':
        ...
    
    @property
    @abc.abstractmethod
    def location_id_protocol(self) -> 'LocationIdentifierProtocol':
        ...

    @property
    @abc.abstractmethod
    def transformation_protocol(
        self
    ) -> 'ContentTransformationProtocol':
        ...
