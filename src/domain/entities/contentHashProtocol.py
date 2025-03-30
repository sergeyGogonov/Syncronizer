import abc
from typing import TYPE_CHECKING, Iterable, Type


if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison
    

class ContentHashProtocol(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def is_compitable_with(
        cls,
        content_hash_protocol: 'Type[ContentHashProtocol]'
    ) -> bool:
        ...

    @abc.abstractmethod
    def get_hash_from_binary(cls, data: bytes) ->  bytes:
        ...

    @abc.abstractmethod
    def get_hash_by_hash_lst(cls, hash_lst: Iterable[bytes]) -> bytes:
        ...
