from collections.abc import Mapping
from typing import Generic, TypeVar


K = TypeVar('K')  # Тип ключа
V = TypeVar('V')  # Тип значения


class ReadOnlyDict(Mapping[K, V], Generic[K, V]):
    def __init__(self, data: dict[K, V] | None):
        self._data = dict(data or {})

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"ReadOnlyDict({self._data})"

    def __hash__(self):
        try:
            return hash(frozenset(self._data.items()))
        except TypeError:
            raise TypeError("ReadOnlyDict contains unhashable elements and cannot be hashed")

    def to_dict(self):
        return dict(self._data)
