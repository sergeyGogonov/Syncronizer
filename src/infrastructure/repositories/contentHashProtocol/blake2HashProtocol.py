from typing import Iterable, Type
from domain.entities.contentHashProtocol import ContentHashProtocol
from hashlib import blake2b


class Blake2ContentHashProtocol(ContentHashProtocol):
    @classmethod
    def is_compitable_with(
        cls,
        content_hash_protocol: 'Type[ContentHashProtocol]'
    ):
        return content_hash_protocol == Blake2ContentHashProtocol

    def get_hash_from_binary(self, data: bytes) ->  bytes:
        hash = blake2b(data, digest_size=32)
        return hash.digest()

    def get_hash_by_hash_lst(self, hash_lst: Iterable[bytes]) -> bytes:
        hash_lst = list(hash_lst)
        hash_lst.sort()
        hash_res = blake2b()
        for hash in hash_lst:
            hash_res.update(hash)
        return hash_res.digest()
