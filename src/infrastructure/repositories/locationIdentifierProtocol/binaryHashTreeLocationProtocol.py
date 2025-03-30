from collections import deque
from typing import Iterator
from domain.entities.dataInfo import DataInfo
from domain.entities.locationIdentifierProtocol import LocationProtocol
from domain.interfaces.tree import Tree


class BinaryHashTreeLocationProtocol(LocationProtocol):
    @classmethod
    def protocol_str_identifier(cls) -> str:
        return 'hashOrderLocation'

    def corvert_tree(self, tree: Tree[DataInfo]) -> Tree[DataInfo]:
        root = tree.root()
        stack: deque[Iterator[DataInfo]] = deque([iter([root])])
        while len(stack) > 0:
            last = stack[-1]
            try:
                cur_child = next(last)
            except StopIteration:
                stack.pop()
                continue
            children = tree.get_children(cur_child)
            if len(children) > 0:
                stack.append(iter(children))
        return
