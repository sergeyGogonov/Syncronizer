from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Iterable, TypeVar
if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison as Comp

#1. Функция, вычисляющая результат на основе данных листа
# Callable[[Leaf, Callable[[Leaf], In]], Out]
#2. Функция сортирующая листы
# Callable[[Leaf], Order]
#3. Функция объединяющаяя результаты
# Callable[[Iterable[Out]], Out]

IN = TypeVar('IN') # Значение в узле, от которого считается функция
OUT = TypeVar('OUT') # Результат функции от узла и его потомков
NODE = TypeVar('NODE') # Тип узла

# TODO: подумать над возможностью дополнительного преобразования
# функции объединения OUT результатов
def DependsOnlyDescendantsListTreeFunctionBuilder(
    get_out_from_in: Callable[[IN], OUT],
    get_in_from_leaf: Callable[[NODE], IN],
    get_leaf_order: Callable[[NODE], 'Comp'],
    get_out_from_ordered_out: Callable[[list[OUT]], OUT],
    get_descendants_method: Callable[[NODE], list[NODE]],
    save_out_method: Callable[[NODE, OUT], None] | None = None,
    get_cached_method: Callable[[NODE], OUT | None] | None = None
) -> Callable[[NODE], OUT]:
    def none_cached(node: NODE):
        return None
    
    # Устанавливаем функцию кэша
    get_cached_method = get_cached_method or none_cached
    
    def foo(node: NODE) -> OUT:
        # Проверяем наличие кэша. Если есть, то возвращаем его
        cached = get_cached_method(node)
        if cached is not None:
            return cached
        # Получаем список потомков
        descendants = get_descendants_method(node)
        # Переменная для результата
        out_res: OUT
        if len(descendants) == 0:
            # Если потомков нет, то считаем результат для текущего узла
            out_res = get_out_from_in(get_in_from_leaf(node))
        else:
            # Если есть потомки, то сортируем их в нужно порядке
            descendants.sort(key=get_leaf_order)
            # Вычисляем выходное значение от каждого узла
            out_results = [foo(desc) for desc in descendants]
            # Вычисляем значения для текущего узла
            out_res = get_out_from_ordered_out(out_results)
        
        # Если нужно сохранить, то сохраняем
        if save_out_method is not None:
            save_out_method(node, out_res)
        return out_res
    # Возвращаем функцию
    return foo   

IN_NODE = TypeVar('IN_NODE')
OUT_NODE = TypeVar('OUT_NODE')

def copy_tree_with_node_tranform_function_builder(
    in_node_leaves_method: Callable[[IN_NODE], Iterable[IN_NODE]],
    out_node_constructor_method: Callable[[IN_NODE], OUT_NODE],
    add_out_node_method: Callable[[OUT_NODE, OUT_NODE], None]
):
    def foo(node: IN_NODE) -> OUT_NODE:
        # Корень результирующего дерева
        out_node_res = out_node_constructor_method(node)
        # Обходим дерево в ширину
        not_visited: deque[tuple[IN_NODE, OUT_NODE]] = deque(((node, out_node_res),))
        while len(not_visited) > 0:
            # Текущие узлы
            in_node, out_node = not_visited.popleft()
            # Узлы на уровень ниже
            for low_in_node in in_node_leaves_method(in_node):
                low_out_node = out_node_constructor_method(low_in_node)
                # Связываем узлы результирующего дерева
                add_out_node_method(out_node, low_out_node)
                # Добавляем узлы в очередь
                not_visited.append((low_in_node, low_out_node))

        return out_node_res

    return foo

# Можно переписать на итераторах        
def bfs_tree_make_operation_function_builder(
    node_leaves_method: Callable[[NODE], Iterable[NODE]],
    operation_method: Callable[[NODE], None]
):
    def foo(node: NODE):
        # Обходим дерево в ширину
        not_visited: deque[NODE] = deque((node,))
        while len(not_visited) > 0:
            # Текущие узлы
            nv_node = not_visited.popleft()
            # Узлы на уровень ниже
            for node_item in node_leaves_method(nv_node):
                # Выполняем операцию над узлом
                operation_method(node_item)
                # Добавляем узлы в очередь
                not_visited.append(node_item)

    return foo        
                
        


