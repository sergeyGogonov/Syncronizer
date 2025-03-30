from typing import TYPE_CHECKING, Sequence

from domain.interfaces.gateway import Gateway
from domain.shared.listTreeFunctionBuilder import DependsOnlyDescendantsListTreeFunctionBuilder, bfs_tree_make_operation_function_builder
from domain.entities.dataInfo import TreeDataInfoWithBinary 

if TYPE_CHECKING:
    from domain.entities.contentHashProtocol import ContentHashProtocol
    from domain.entities.contentTransformationProtocol import ContentTransformationProtocol
    from domain.entities.locationIdentifierProtocol import LocationIdentifierProtocol

from pathlib import Path
from domain.interfaces.gateway import BadLocationId, NoContentFromLocationId
from infrastructure.repositories.osFileSystem.dataInfo import OsDirectoryDataInfo, OsFileDataInfo, OsFileObjectDataInfo
import xattr

# TODO: подумать как защитить от возможности проникнуть в другие каталоги при помощи
# ../ и ./
class OsFileSystemGateway(Gateway):
    def __init__(
        self,
        location_id_protocol: 'LocationIdentifierProtocol',
        hash_protocol: 'ContentHashProtocol',
        transformation_protocol: 'ContentTransformationProtocol',
        abs_root_dir_path: str
    ):
        self._root_dir_path = Path(abs_root_dir_path.rstrip('/') + '/')
        self._check_root_path()
        
        super().__init__(location_id_protocol, hash_protocol, transformation_protocol)
        
        # Собираем функцию, вычисляющуюю хэши. Вычисляем хэши
        self._hash_tree_calculator = self._get_hash_tree_calculator()
        self._calculate_hash_tree()
        # Собираем функцию, сохраняющую файлы
        self._save_tree = self._get_save_tree_function()

    def get_binary_by_id(self, location_id: str) -> bytes:
        path = self._get_path_by_rel_path(location_id)
        if path.is_dir():
            return b''
        elif path.is_file():
            return path.read_bytes()
        else:
            raise Exception(
                'Работаем только с файлами и каталогами!'
                f'location_id={location_id}'
            )
    # TODO: добавить обработку location_id
    def get_content_by_id(self, location_id: str) -> 'TreeDataInfoWithBinary':
        rel_path = location_id
        d_info = self._make_d_info_from_rel_path(rel_path)
        
        return d_info

    def get_root(self) -> 'TreeDataInfoWithBinary':
        return self._make_d_info_from_rel_path('')

    def _make_d_info_from_rel_path(self, rel_path: str):
        path = self._get_path_by_rel_path(rel_path)
        is_dir = path.is_dir()
        if is_dir:
            d_info_cls = OsDirectoryDataInfo
            meta_info = None
        else:
            d_info_cls = OsFileDataInfo
            meta_info = None
        hash = self._get_hash_by_path(path)
        assert hash is not None
        return d_info_cls(self, rel_path, hash, meta_info)

    def _make_dir(self, path: Path):
        assert path.is_dir()
        meta_info = {
            'content-length': path.stat().st_size
        }
        content_list = [item for item in path.iterdir()]
        content_list.sort(
            key=lambda path: (str(path))
        )
    
    def _calculate_hash_tree(self):
        self._hash_tree_calculator(self._root_dir_path)

    def _get_internal_paths_by_path(self, path: Path) -> list[Path]:
        content_lst = []
        if path.is_dir():
            for item in path.iterdir():
                self._check_path(item)
                content_lst.append(item)
        return content_lst 
    
    def _get_hash_tree_calculator(self):
        def get_path_order(path: Path):
            return str(path)

        return DependsOnlyDescendantsListTreeFunctionBuilder(
            # Функция, хэширующая бинарник
            self._hash_protocol.get_hash_from_binary,
            # Функция, извлекающая бинарник
            Path.read_bytes, 
            # Функция, для упорядочивания путей в директории
            get_path_order,
            # Функция, для вычисления хэшей от вычисленных хэшей 
            self._hash_protocol.get_hash_by_hash_lst,
            # Функция, для извлечения путей внутри директории
            self._get_internal_paths_by_path,
            # Функция, сохраняющая хэши в файловой системе
            self._save_hash_by_path,
            # Функция, возвращающая сохраненный хэш
            self._get_hash_by_path
        )
    
    # TODO: обработать исключения
    def _save_hash_by_path(self, path: Path, hash: bytes):
        xattr.setxattr(str(path), 'user.hash', hash)
    
    # TODO: подумать над исключениями
    def _get_hash_by_path(self, path: Path) -> bytes | None:
        try:
            return xattr.getxattr(str(path), 'user.hash')
        except IOError:
            return None

    def _get_path_by_rel_path(self, rel_path: str) -> Path:
        path = Path(self._root_dir_path / rel_path)
        if not path.exists():
            raise NoContentFromLocationId(
                f'location_id={self._get_rel_path_by_path(path)}'
            )
        if not (path.is_dir() or path.is_file()):
            raise Exception(
                'Работаем только с файлами и каталогами!'
                f'location_id={rel_path}'
            )
        return path

    def get_internal_content_by_id(
        self,
        location_id: str
    ) -> Sequence['TreeDataInfoWithBinary']:
        dir_path = self._get_path_by_rel_path(location_id)
        return [ 
            self._make_d_info_from_rel_path(self._get_rel_path_by_path(path))
                for path in self._get_internal_paths_by_path(dir_path)
        ]
    # TODO: нужен класс, который не имеет идентификатора
    def save_content_by_id(
        self, 
        location_id: str,
        d_info: 'TreeDataInfoWithBinary'
    ) -> bool:
        rel_path = location_id
        self._get_path_by_rel_path(rel_path)
        self._save_tree(d_info)
        return True
        
    def _save_by_path(self, path: Path, data: bytes):
        if str(path).endswith('/'):
            return
        path.touch()
        path.write_bytes(data)
    
    
    #TODO: Добавить преобразование идентификатора
    def _save_by_d_info(
        self,
        d_info: 'TreeDataInfoWithBinary'
    ):
        path = self._get_path_by_rel_path(d_info.location_id)
        self._save_by_path(path, d_info.get_binary())
        
    
    def _get_save_tree_function(self):
        data_cls = TreeDataInfoWithBinary
        return bfs_tree_make_operation_function_builder(
            # Метод вычисляющий потомков
            data_cls.get_internal_content,
            # Операция сохранения
            self._save_by_d_info
        )

    # TODO: записывать информацию в конструкторе
    def is_empty_binary(self, file_d_info: OsFileDataInfo):
        path = self._get_path_by_rel_path(file_d_info.rel_path)
        return path.stat().st_size
        
    def _check_root_path(self): 
        if not self._root_dir_path.is_absolute():
            raise ValueError(
                'Передан не абсолютный путь!'
                f'root_dir_path={str(self._root_dir_path)}'
            )

    def _check_path(self, path):
        if not (path.is_dir() or path.is_file()):
            raise Exception(
                'Работаем только с файлами и каталогами!'
            )
        return path

            

    def _get_rel_path_by_path(self, path: Path) -> str:
        self._root_dir_path.parent
        rel_path = path.relative_to(self._root_dir_path)
        return str(rel_path)

    @property
    def location_id_protocol(self):
        return self._location_id_protocol

    @property
    def hash_protocol(self):
        return self._hash_protocol

    @property
    def transformation_protocol(self):
        return self._transformation_protocol

    
    
    
    
