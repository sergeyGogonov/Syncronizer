from domain.entities.dataInfo import TreeDataInfoWithBinary
from domain.interfaces.gateway import Gateway


class FileObjectDataInfo(TreeDataInfoWithBinary):
    def __init__(
        self,
        gateway: 'Gateway',
        location_id: str,
        hash_str: bytes,
        meta_data: dict[str, str] | None = None
    ):
        super().__init__(gateway, location_id, hash_str, meta_data)
        

class FileDataInfo(FileObjectDataInfo):
    def is_empty_binary(self) -> bool:
        length = self.meta_data.get('content_length')
        if (
            (length is not None)
            and length.isdecimal() 
            and int(length) == 0
        ):
            return True
        else:
            return False

    def may_has_internal_content(self) -> bool:
        return False


class DirectoryDataInfo(FileObjectDataInfo):
    def is_empty_binary(self) -> bool:
        return True

    def may_has_internal_content(self) -> bool:
        return True
