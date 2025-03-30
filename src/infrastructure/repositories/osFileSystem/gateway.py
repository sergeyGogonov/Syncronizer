from enum import Enum
from io import BufferedReader
from pathlib import Path
from typing import Any, Callable, ContextManager, Generic, Optional, Sequence, TypeVar
from domain.entities.contentTransformationProtocol import DataTransformationProtocol
from domain.entities.dataInfo import IdentifiedInfo
from domain.entities.locationIdentifierProtocol import LocationProtocol
from domain.interfaces.gateway import GatewayFactory, IdNotFoundError, ModifiableTreeDataGateway, ReadableTreeDataGateway, TreeDataGateway
import itertools
import threading

from infrastructure.repositories.contentHashProtocol.blake2HashProtocol import Blake2ContentHashProtocol
from infrastructure.repositories.contentTransformationProtocol.identityTransformation import IdentityTransformationProtocol
from infrastructure.repositories.locationIdentifierProtocol.relPathLocationIdentifierProtocol import RelPathLocationIdentifierProtocol


# Пока что id-шки будут генерироваться динамически
# Пока что будем всегда читать напрямую с диска
# TODO: подумать, как оповещать factory без прямой ссылки
class OsGateway(TreeDataGateway):
    ...


class OsReadableGateway(ReadableTreeDataGateway, OsGateway):
    def __init__(
        self,
        os_gate_fact: 'OsGatewayFactory'
    ):
        self._os_gate_fact = os_gate_fact

    def get_root(self) -> IdentifiedInfo:
        root_id = self._os_gate_fact.root_id
        return self._os_gate_fact.get_identified_info(root_id)

    def get_info_by_id(self, id: int) -> IdentifiedInfo:
        return self._os_gate_fact.get_identified_info(id)

    def get_childs_info_by_id(self, id: int) -> Sequence[IdentifiedInfo]:
        return self._os_gate_fact.get_childs_by_id(id)

    def get_binary_data_by_id(self, id: int) -> BufferedReader:
        return self._os_gate_fact.get_binary_by_id(id)

    def get_hash_protocol(self):
        return self._os_gate_fact.get_hash_protocol()

    def get_location_protocol(self) -> 'LocationProtocol':
        return self._os_gate_fact.get_location_protocol()
        
    def get_data_transformation_protocol(self) -> 'DataTransformationProtocol':
        return self._os_gate_fact.get_trans_protocol()


class OsModifiableGateway(ReadableTreeDataGateway, OsGateway):
    ...


class LockStateError(Exception):
    ...


class TriedAction(Enum):
    NO_ACTION = 0
    ENTER = 1
    EXIT = 2

T = TypeVar('T', bound=OsGateway)

class OsGatewayContextManager(ContextManager[T], Generic[T]):
    def __init__(
        self,
        gate: T,
        update_method: 'Callable[[OsGatewayContextManager]]'
    ):
        self._gate = gate
        self._update_method = update_method
        self._gate_kls = gate.__class__
        self._tried_action = TriedAction.NO_ACTION

    @property
    def gate_kls(self):
        return self._gate_kls
    
    # Возвращает попытку действия
    @property
    def tried_action(self):
        tried_act = self._tried_action
        self._tried_action = TriedAction.NO_ACTION
        return tried_act

    def __enter__(self) -> T:
        self._tried_action = TriedAction.ENTER
        # Уведомляем о выдаче доступа
        self._update_method(self)
        return self._gate

    # TODO: нужно ли здесь try?
    def __exit__(self, param, par, pa):
        self._tried_action = TriedAction.EXIT
        self._update_method(self)


class GatewayAccessError(Exception):
    ...


class ReadingNotAllowedError(GatewayAccessError):
    ...


class ModifeingNotAllowedError(GatewayAccessError):
    ...


class ReadWriteLock:
    def __init__(self):
        self._read_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._readers_count = 0

    def acquire_read(self):
        with self._read_lock:
            self._readers_count += 1
            if self._readers_count == 1:
                self._write_lock.acquire()

    def release_read(self):
        with self._read_lock:
            self._readers_count -= 1
            if self._readers_count == 0:
                self._write_lock.release()

    def acquire_write(self):
        self._write_lock.acquire()

    def release_write(self):
        self._write_lock.release()

    @property
    def read_locked(self):
        return self._read_lock.locked()

    @property
    def write_locked(self):
        return self._write_lock.locked()


class PathWithChilds:
    def __init__(
        self,
        path: Path,
        childs: Optional[list[int]] = None
    ):
        self._childs = childs
        self._path = path

    @property
    def childs(self) -> Optional[list[int]]:
        return self._childs

    @property
    def path(self):
        return self._path

    @childs.setter
    def childs(self, childs: list[int]):
        self._childs = childs 


class OsGatewayFactory(GatewayFactory):
    def __init__(
        self,
        abs_root_dir_path: str
    ):
        # TODO: оформить в отдельный класс
        # Инициализация генератора идентификаторов для инициализации каталога
        self._id_generator = itertools.count(start=0)
        self._next_id = next(self._id_generator)
        # Временно словарь с идентификаторами
        self._path_id = {}
        # Инициализация словаря с путями
        self._id_path_dict: dict[int, PathWithChilds] = {}
        # Инициализация корневого каталога
        self._root_id = self._mark_path_with_id(
            self._get_root_path_by_abs(abs_root_dir_path)
        )
        # Инициализация для доступа к чтению-изменению
        self._locker = ReadWriteLock()
        self._active_mngs: set[OsGatewayContextManager] = set()
        
        # TODO: можно сохранить в метаинформации
        # Назначаем hash-протокол
        self._hash_prototol = Blake2ContentHashProtocol()
        # Назначаем LocationProtocol
        self._location_protocol = RelPathLocationIdentifierProtocol()
        # Назначаем 
        self._content_trans_protocol = IdentityTransformationProtocol()

    @property
    def root_id(self):
        return self._root_id

    @property
    def _root_path(self):
        return self._id_path_dict[self._root_id].path
    
    def _manage_lock(self, gate_mng: 'OsGatewayContextManager'):
        if gate_mng.tried_action == TriedAction.ENTER:
            if issubclass(gate_mng.gate_kls, OsReadableGateway):
                try:
                    self._locker.acquire_read()
                except RuntimeError as e:
                    raise ReadingNotAllowedError(e)
            elif issubclass(gate_mng.gate_kls, OsModifiableGateway):
                try:
                    self._locker.acquire_write()
                except RuntimeError as e:
                    raise ModifeingNotAllowedError(e)
        elif gate_mng.tried_action == TriedAction.EXIT:
            if issubclass(gate_mng.gate_kls, OsReadableGateway):
                self._locker.release_read()
            elif issubclass(gate_mng.gate_kls, OsModifiableGateway):
                self._locker.release_write()
    
    # Возвращает абсолютный путь до корневого каталога
    def _get_root_path_by_abs(self, abs_root_dir_path: str):
        root_path = Path(abs_root_dir_path.rstrip('/'))
        if not root_path.is_absolute():
            raise ValueError(
                'Передан не абсолютный путь!'
                f'abs_root_dir_path={abs_root_dir_path}'
            )
        if not root_path.is_dir():
            raise ValueError(
                'Путь должен указывать на директорию!'
                f'abs_root_dir_path={abs_root_dir_path}'
            )
        return root_path

    def _get_path_by_id(self, id: int):
        return self._id_path_dict[id]
    
    # Вызывается для всякого пути
    def _mark_path_with_id(self, path: Path) -> int:
        cur_id = self._next_id
        self._id_path_dict[cur_id] = PathWithChilds(path)
        self._path_id[str(path)] = cur_id
        self._next_id = next(self._id_generator)
        return cur_id

    # Для выдачи новых путей используется только эта функция 
    # Путь получает идентификатор, как только кто-то его нашел
    def _get_childs_by_path(
        self,
        path: Path,
    ) -> list[tuple[Path, int]]:
        self._is_good_path(path)
        res: list[tuple[Path, int]] = []
        if path.is_file():
            return res
        for item in path.iterdir():
            id = self._mark_path_with_id(item)
            res.append((item, id))
        return res


    def _update_identified_info_by_id(self, id: int):
        cpath = self._id_path_dict.get(id)
        if not cpath:
            raise IdNotFoundError('Неизвестный идентификатор!')
        return IdentifiedInfo(
            id,
            self._get_meta_info_by_path(cpath.path)
        )

    # TODO: если путь еще не посещен, то у него может не быть id-шника
    # Для выдачи IdentifiedInfo по id (обновленного)
    def get_identified_info(self, id) -> IdentifiedInfo:
        return self._update_identified_info_by_id(id)

    def get_childs_by_id(self, id: int) -> Sequence[IdentifiedInfo]:
        cpath = self._id_path_dict.get(id)
        if not cpath:
            raise IdNotFoundError('Неизвестный идентификатор!')
        if cpath.childs is None:
            # Если пути не идентифицированы
            res = []
            childs_ids = []
            for item, id in self._get_childs_by_path(cpath.path):
                # print('ffff', item)
                res.append(IdentifiedInfo(id, self._get_meta_info_by_path(item)))
                childs_ids.append(id)
            cpath.childs = childs_ids
        else:
            # Если пути идентифицированы
            res = [
                IdentifiedInfo(
                    id, self._get_meta_info_by_path(self._id_path_dict[id].path)
                ) for id in cpath.childs
            ]
        return res
     
    def _is_good_path(self, path: Path):
        if not (
            path.is_file() 
            or path.is_dir()
        ):
            raise Exception('В директории должны находиться только файлы и папки!')
        return path

    def _check_readability(self) -> bool:
        return True

    def _check_modifiablility(self) -> bool:
        return True
 
    def _get_meta_info_by_path(self, path: Path) -> dict[str, Any]:
        return {
            'hashOrderLocation': self._path_id[str(path)],
            'rel_path': str(path.relative_to(self._root_path))
        }

    def get_binary_by_id(self, id: int):
        cpath  = self._id_path_dict.get(id)
        if not cpath:
            raise IdNotFoundError('Неизвестный идентификатор!')
        return cpath.path.open('rb')

    def get_hash_protocol(self):
        return Blake2ContentHashProtocol()

    def get_location_protocol(self):
        return self._location_protocol

    def get_trans_protocol(self):
        return self._content_trans_protocol
        
    def _get_elem_from_path(self):
        ...

    # Создает нового независимого чтеца с общей индексацией
    def _build_readable_gateway_context_manager(self):
        return OsGatewayContextManager(
            OsReadableGateway(self),
            self._manage_lock
        )
    
    def get_readable_gateway(
        self,
        location_protocol: 'Optional[LocationProtocol]' = None
    ) -> 'ContextManager[ReadableTreeDataGateway]':
        return self._build_readable_gateway_context_manager()


    def get_modifiable_gateway(
        self,
        location_protocol: 'Optional[LocationProtocol]' = None
    ) -> 'ContextManager[ModifiableTreeDataGateway]':
        ...



    

