import abc
from collections import deque
from typing import Callable, Iterable, Iterator, TypeVar, Generic, Optional, List

T = TypeVar('T')
CT = TypeVar('CT')

class Tree(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def root(self) -> T:
        ...

    @abc.abstractmethod
    def find_node(self, node: T) -> Optional[T]:
        ...

    @abc.abstractmethod
    def get_children(self, node: T) -> list[T]:
        ...

    def tree_repr_from_node(
        self,
        node: T,
        to_str_foo: Callable[[T], str] = repr,
        indent: str = '  ',
    ):
        stack: deque[Iterator[T]] = deque([iter([node])])
        res_items: list[str] = []
        while len(stack) > 0:
            last = stack[-1]
            try:
                cur_child = next(last)
            except StopIteration:
                stack.pop()
                continue
            children = self.get_children(cur_child)
            res_items.append(indent * (len(stack) - 1) + to_str_foo(cur_child) + '\n')
            if len(children) > 0:
                stack.append(iter(children))
        return ''.join(res_items)
    

class ReadOnlyTree(Tree[T], Generic[T]):
    ...

class ModifiableTree(Tree[T], Generic[T]):
    @abc.abstractmethod
    def add_node(self, p_node: T, c_node: 'T'):
        ...

    @abc.abstractmethod
    def remove_node(self, node: T):
        ...

class TreeKeeper(abc.ABC, Generic[T, CT]):
    @abc.abstractmethod
    def keep(self, tree: ReadOnlyTree[T]) -> ReadOnlyTree[CT]:
        ...

class TreeError(Exception):
    ...

class NodeNotFoundedError(Exception):
    ...

    


