import abc
from enum import Enum
from pathlib import Path
from typing import ContextManager, Generic, Optional, TypeVar
from domain.interfaces.gateway import GatewayFactory, ReadableTreeDataGateway, TreeDataGateway

class OneFileGatewayError(Exception):
    ...

class ClosedBeforeOpenedError(OneFileGatewayError):
    ...

class NotExpectedGatewayTypeError(OneFileGatewayError):
    ...

class NotExpectedFileModeError(OneFileGatewayError):
    ...

class OneFileGateway(TreeDataGateway, ContextManager[TreeDataGateway]):
    def __init__(self, abs_file_path: str, mode: str):
        self._file_path = Path(abs_file_path)
        self._mode = mode
        assert self._file_path.is_file()
    
        if mode not in ['r', 'w']:
            raise NotExpectedFileModeError()
        

    def __enter__(self) -> 'OneFileGateway':
        self._file_obj = self._file_path.open(self._mode)
        return self
    
    def __exit__(self, pa, par, para):
        if self._file_obj is None:
            raise ClosedBeforeOpenedError()
        self._file_obj.close()


class OneFileReadableGateway(ReadableTreeDataGateway, OneFileGateway):
    ...

class OneFileGatewayFactory(GatewayFactory):
    def __init__(self, abs_file_path: str):
        self._file_path = Path(abs_file_path)
        if self._file_path.is_absolute():
            raise Exception(f'Путь долен быть абсолютным!\nfile_path={abs_file_path}')
        if self._file_path.is_file():
            raise FileNotFoundError(f'file_path={abs_file_path}')
    

        
