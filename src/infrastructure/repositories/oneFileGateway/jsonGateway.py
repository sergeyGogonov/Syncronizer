from io import BufferedReader
from pathlib import Path
from typing import Any, Sequence
from domain.entities.contentHashProtocol import ContentHashProtocol
from domain.entities.contentTransformationProtocol import DataTransformationProtocol
from domain.entities.dataInfo import IdentifiedInfo
from domain.entities.locationIdentifierProtocol import LocationProtocol
from infrastructure.repositories.oneFileGateway.gateway import OneFileGateway

import json


class JsonGateway(OneFileGateway):
    def __init__(self, abs_file_path, mode: str):
        super().__init__(abs_file_path, mode)
        self._full_dict: dict[str, dict[int, Any]]
        self._tree_dict: dict[int, dict[str, Any]]
    
    def _build_from_dict(self):
        self._tree_dict = self._full_dict['root']

    def __enter__(self) -> 'OneFileGateway':
        super().__enter__()
        self._full_dict = json.load(self._file_obj)
        self._tree_dict = self._full_dict['root']
        return self

    def __exit__(self, pa, par, para):
        del self._full_dict
        del self._tree_dict
        return super().__exit__(pa, par, para)

    def get_root(self) -> 'IdentifiedInfo':
        ...

    def get_binary_data_by_id(self, id: int) -> 'BufferedReader':
        ...

    def get_childs_info_by_id(self, id: int) -> 'Sequence[IdentifiedInfo]':
        ...

    def get_data_transformation_protocol(self) -> 'DataTransformationProtocol':
        ...

    def get_hash_protocol(self) -> 'ContentHashProtocol':
        ...

    def get_info_by_id(self, id: int) -> 'IdentifiedInfo':
        ...

    def get_location_protocol(self) -> 'LocationProtocol':
        ...
