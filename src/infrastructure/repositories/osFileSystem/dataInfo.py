from typing import TYPE_CHECKING, Sequence
from infrastructure.repositories.filesAndDirectories.dataInfo import DirectoryDataInfo, FileDataInfo, FileObjectDataInfo

if TYPE_CHECKING:
    from infrastructure.repositories.osFileSystem.gateway import OsFileSystemGateway


class OsFileObjectDataInfo(FileObjectDataInfo):
    ...

class OsFileDataInfo(FileDataInfo):
    ...

class OsDirectoryDataInfo(DirectoryDataInfo):
    ...
