""" Параллельные процессы """
import dill
from multiprocessing import Process, Manager, Semaphore
from typing import List, Optional, Callable, Any, Dict

# формат списка задач
TTasksList = Optional[List[Any]]


def do_task(num: int, semaphore: Semaphore, func: Callable, data: Any, result: Dict):
    """ Обертка над выполняемой функцией, использующая семафор, чтобы избежать конфликтов

    Args:
        num: номер задачи (используется как ключ в результирующем словаре)
        semaphore: семафор
        func: исполняемая функция
        data: данные, передаваемые исполняемой функции на вход
        result: результирующий словарь вида {номер_задачи: результат_выполнения_задачи}
    """
    semaphore.acquire()
    args = [data] if data is not None else []
    result[num] = func(*args)
    semaphore.release()


class DillProcess(Process):
    """ Обертка над стандартным питонячьим Процессом, использующая dill-сериализацию (считает лучше, чем pickle) """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # сериализация исполняемой функции с помощью dill
        self._target = dill.dumps(self._target)

    def run(self):
        if not self._target:
            return
        # десериализация исполняемой функции с помощью dill и ее исполнение
        self._target = dill.loads(self._target)
        self._target(*self._args, **self._kwargs)


class ParallelWorker:
    """ Отвечает за распараллеливание неконкурирующих задач.

     Например, у нас есть 1000 задач, которые нужно выполнить.
     При инициализации задаем processes = 5.
     За один раз будет выполняться не более 5 задач, остальные будут ждать в очереди.

     На вход отдаем исполняемую функцию (обязательно должна уметь принимать хотя бы один аргумент) и "список задач",
     то есть список кортежей аргументов для всего пула задач.

     На выходе получаем словарь вида {номер_задачи: результат_выполнения_задачи}
     """

    def __init__(self, processes: int = 3):
        """
        Args:
            processes: количество одновременных процессов
        """
        self.__processes = processes

    def start(self, func: Callable, tasks_list: TTasksList = None) -> Dict:
        """ Исполняемая функция и список задач.

        Args:
            func: исполняемая функция (обязательно должна уметь принимать хотя бы один аргумент)
            tasks_list: список с данными для задачи

        Returns:
            словарь вида {номер_задачи: результат_выполнения_задачи}

        Notes:
            Если список задач не задан, то функция исполняется без параметров параллельно по числу процессов.
        """
        # менеджер процессов, который обеспечивает решение конфликтов доступа к разделяемой памяти
        #   и семафор, который разруливает конфликты между процессами в ходе исполнения функции
        manager = Manager()
        result = manager.dict()
        semaphore = Semaphore(self.__processes)
        # список входных параметров должен быть всегда чем-то заполнен, хотя бы так [None, None ...]
        if not tasks_list:
            tasks_list = [None for _ in range(self.__processes)]
        # здесь все по классике с тем лишь исключением, что мы используем обертку DillProcess вместо Process
        all_processes = []
        for num, data in enumerate(tasks_list or []):
            p = DillProcess(target=do_task, args=(num, semaphore, func, data, result))
            all_processes.append(p)
            p.start()
        # ожидаем завершения всех параллельных процессов и возвращаем результат
        for p in all_processes:
            p.join()
        return result
