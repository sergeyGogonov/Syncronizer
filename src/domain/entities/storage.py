from typing import TYPE_CHECKING, ContextManager, Optional

from domain.entities.dataInfo import DataInfo
from domain.interfaces.gateway import ReadableTreeDataGateway
from domain.interfaces.tree import ReadOnlyTree


if TYPE_CHECKING:
    from domain.entities.dataInfo import DataInfoBuilder, abc
    from domain.entities.locationIdentifierProtocol import LocationProtocol
    from domain.entities.mirrorGatewayTree import MirrorGatewayTree
    from domain.interfaces.tree import TreeKeeper
    from domain.interfaces.gateway import GatewayFactory

class StorageTreeManager:
    def __init__(
        self,
        gateway_factory: GatewayFactory,
        d_info_builder: DataInfoBuilder,
        tree_converter: Optional[TreeKeeper] = None,
        loc_protocol: Optional[LocationProtocol] = None,
    ):
        self._gateway_factory: GatewayFactory = gateway_factory
        self._tree_converter = tree_converter
        self.loc_protocol = loc_protocol
        self._d_info_builder = d_info_builder

        self._active_read_man: Optional[ContextManager[ReadableTreeDataGateway]] = None


    def __enter__(self) -> ReadOnlyTree[DataInfo]:
        r_gate_manager = self._gateway_factory.get_readable_gateway(self.loc_protocol)
        r_gate = r_gate_manager.__enter__()
        mirr_tree = MirrorGatewayTree(r_gate, self._d_info_builder)
        if self._tree_converter:
            self._root = self._tree_converter.convert(mirr_tree)
        else:
            self._active_read_man = r_gate_manager
            self._root = mirr_tree
        
        return self._root


    @abc.abstractmethod
    def __close__(self):
        if self._active_read_man:
            self._active_read_man.__exit__(None, None, None)
            self._active_read_man = None


    


