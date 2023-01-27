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
    # пример использования
    tasks_list = list(range(50))
    result: Dict = ParallelWorker(processes=5).start(
        func=some_work_to_do,
        tasks_list=tasks_list
    )
    for key, value in result.items():
        print(f'{key} :: {value}')
