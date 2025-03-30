from typing import ContextManager, Generic, TypeVar
from domain.entities.dataInfo import DataInfo, DataInfoBuilder
from domain.interfaces.gateway import ModifiableTreeDataGateway, ReadableTreeDataGateway
from domain.interfaces.tree import ModifiableTree, NodeNotFoundedError, ReadOnlyTree, Tree


class DirectGatewayTree(Tree[DataInfo]):
    def __init__(
        self,
        r_gate: 'ReadableTreeDataGateway',
        d_info_builder: 'DataInfoBuilder'
    ):
        self._r_gate = r_gate
        self._d_info_builder = d_info_builder
        self._root = d_info_builder.build(r_gate.get_root())
    
    def root(self):
        return self._d_info_builder.build(
            self._r_gate.get_info_by_id(self._r_gate.get_root().id)
        )

    def find_node(self, node: 'DataInfo'):
        return self._d_info_builder.build(
            self._r_gate.get_info_by_id(node.id)
        )

    def get_binary_file(self, node: 'DataInfo'):
        return self._r_gate.get_binary_data_by_id(node.id)

    def get_children(self, node: 'DataInfo'):
        return [ self._d_info_builder.build(item) 
            for item in self._r_gate.get_childs_info_by_id(node.id)
        ]


class DirectGatewayReadOnlyTree(DirectGatewayTree):
    ...
    

class DirectGatewayModifiableTree(DirectGatewayTree, ModifiableTree[DataInfo]):
    def __init__(
        self,
        m_gate: 'ModifiableTreeDataGateway',
        d_info_builder: 'DataInfoBuilder'
    ):
        self._d_info_builder = d_info_builder
        self._root = d_info_builder.build(m_gate.get_root())
        self._m_gate = m_gate
    
    def add_node(self, p_node: 'DataInfo', c_node: 'DataInfo'):
        # Получаем id для контента
        id_for_file = self._m_gate.get_id_for_new_elem(p_node.id)
        # Получаем файловый менеджер
        b_data_keeper = c_node.b_data_keeper
        # Если он пуст, то финита ля комедия
        if not b_data_keeper.is_keeped():
            raise ValueError('Невозможно получить данные!')
        # Передаем файл на сохранение
        with b_data_keeper.keeped_data as file:
            self._m_gate.save_data_by_id(
                id_for_file,
                file,
                c_node.meta_info
            )

    def remove_node(self, node: 'DataInfo'):
        self._m_gate.delete_by_id(node.id)


        


