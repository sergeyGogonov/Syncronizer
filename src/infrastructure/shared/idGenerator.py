import itertools

class Node:
    def __init__(self, data, children=None):
        self.data = data
        self.children = children if children is not None else []
        self.id = None  # Идентификатор изначально не задан

    def assign_ids(self, id_generator, id_map):
        """
        Лениво присваивает ID узлу и его потомкам.

        Args:
            id_generator: Генератор уникальных ID (например, itertools.count).
            id_map: Словарь для хранения соответствия ID -> узел.
        """
        if self.id is None: #ленивая генерация
            self.id = next(id_generator)
            id_map[self.id] = self

        for child in self.children:
            child.assign_ids(id_generator, id_map)

# Пример использования:
# Создаем дерево
root = Node("A", [
    Node("B", [Node("D"), Node("E")]),
    Node("C", [Node("F")])
])

# Генератор ID и словарь для быстрого доступа
id_gen = itertools.count(start=1)  # Начинаем с 1 (или любого другого значения)
node_map = {}

# Присваиваем ID (лениво, при первом обращении)
root.assign_ids(id_gen, node_map)

# Доступ к узлам по ID:
print(f"Узел с ID 3: {node_map.get(3).data if 3 in node_map else 'Not Found'}")  # Быстрый доступ! O(1)
print(f"Узел с ID 1: {node_map.get(1).data if 1 in node_map else 'Not Found'}")
print(f"Узел с ID 7: {node_map.get(7).data if 7 in node_map else 'Not Found'}") # Такого узла нет

# Доступ к ID узла
print(f"ID узла root: {root.id}")
print(f"ID узла B: {root.children[0].id}")


#Пример с ленивым вычислением идентификатора
another_root = Node("Root")
id_gen2 = itertools.count(start=1)
node_map2 = {}

print(f"ID another_root (before assignment): {another_root.id}")  # None
another_root.assign_ids(id_gen2, node_map2) #произошло присвоение id
print(f"ID another_root (after assignment): {another_root.id}")  # 1
print(f"Узел с ID 1: {node_map2[1].data}") # Root
