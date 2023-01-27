ParallelWorker

    Отвечает за распараллеливание неконкурирующих задач.
    
    Например, у нас есть 50 задач, которые нужно выполнить.
    При инициализации задаем processes = 5.
    За один раз будет выполняться не более 5 задач, остальные будут ждать в очереди.
    
    На вход отдаем исполняемую функцию и "список задач",
    то есть список кортежей аргументов для всего пула задач.
    
    На выходе получаем словарь вида {номер_задачи: результат_выполнения_задачи}

Пример использования

```
from typing import Optional, Dict
from utils.worker.parallel import ParallelWorker


def some_work_to_do(x: Optional[int] = None) -> Optional[int]:
    """ Функция, выполняющая какую-либо полезную работу в нескольких процессах

    Args:
        x: число аргументов может быть любым, но хотя бы один аргумент обязателен [!]

    Returns:
        Any

    Notes:
        функция должна быть доступна извне, это значит, что, например, private-метод использовать не получится [!]
    """
    if x is None:
        return None
    return x * 2


if __name__ == '__main__':
    tasks_list = list(range(50))
    result: Dict = ParallelWorker(processes=5).start(
        func=some_work_to_do,
        tasks_list=tasks_list
    )
    for key, value in result.items():
        print(f'{key} :: {value}')

```