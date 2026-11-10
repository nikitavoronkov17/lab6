"""
Лабораторная работа № 6. Вариант 5.
Односвязный список, очередь на списке.
Исследуемые операции: доступ по индексу, удаление из середины.
Размеры n = 1000, 2000, 4000.
Прикладная задача — журнал операций с правками.

Всё в одном файле: односвязный список, очередь на списке, журнал
операций, замеры, проверка памяти, графики.
Внешняя зависимость — только matplotlib.
"""
import sys
import time


# ==================== Узел и односвязный список ====================

class Node:
    """Узел односвязного списка."""
    __slots__ = ("value", "next")

    def __init__(self, value, nxt=None):
        self.value = value
        self.next = nxt


class LinkedList:
    """Односвязный список со ссылкой на хвост."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def push_back(self, value):
        """Вставка в конец — Θ(1) благодаря tail."""
        node = Node(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def push_front(self, value):
        """Вставка в начало — Θ(1)."""
        self.head = Node(value, self.head)
        if self.tail is None:
            self.tail = self.head
        self.size += 1

    def get(self, index):
        """Доступ по индексу — Θ(index)."""
        if not 0 <= index < self.size:
            raise IndexError("Индекс вне диапазона")
        node = self.head
        for _ in range(index):
            node = node.next
        return node.value

    def remove_at(self, index):
        """Удаление по индексу — Θ(index) на поиск + Θ(1) на перестановку."""
        if not 0 <= index < self.size:
            raise IndexError("Индекс вне диапазона")
        if index == 0:
            value = self.head.value
            self.head = self.head.next
            if self.head is None:
                self.tail = None
        else:
            prev = self.head
            for _ in range(index - 1):
                prev = prev.next
            value = prev.next.value
            prev.next = prev.next.next
            if prev.next is None:
                self.tail = prev
        self.size -= 1
        return value

    def to_list(self):
        result, node = [], self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

    def __len__(self):
        return self.size


# ==================== Очередь на связном списке ====================

class ListQueue:
    """Очередь (FIFO) на основе односвязного списка."""

    def __init__(self):
        self.list = LinkedList()

    def enqueue(self, value):
        """Постановка в очередь — Θ(1)."""
        self.list.push_back(value)

    def dequeue(self):
        """Извлечение из очереди — Θ(1)."""
        if self.list.size == 0:
            raise IndexError("Очередь пуста")
        return self.list.remove_at(0)

    def __len__(self):
        return self.list.size

    def to_list(self):
        return self.list.to_list()


# ==================== Замер ====================

def measure(action, repeats=3):
    """Медианное время выполнения action(), с."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        action()
        times.append(time.perf_counter() - start)
    times.sort()
    return times[len(times) // 2]


# ==================== Прикладная задача ====================

class OperationJournal:
    """Журнал операций с правками.
    Поддерживает: append, get, delete, cancel_last.
    """

    def __init__(self):
        self._list = LinkedList()

    def append(self, op):
        self._list.push_back(op)

    def get(self, index):
        return self._list.get(index)

    def delete(self, index):
        return self._list.remove_at(index)

    def cancel_last(self):
        if self._list.size == 0:
            raise IndexError("Журнал пуст")
        return self._list.remove_at(self._list.size - 1)

    def __len__(self):
        return self._list.size

    def __repr__(self):
        return f"OperationJournal({self._list.to_list()})"


# ==================== Эксперимент ====================

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # ---------- Т1: корректность на малом примере ----------
    print("--- Т1: проверка корректности на малом примере ---")
    lst = LinkedList()
    for v in [10, 25, 7, 33, 18]:
        lst.push_back(v)
    print("Список после push_back:", lst.to_list())
    print("lst.get(2) =", lst.get(2))
    print("lst.remove_at(2) =", lst.remove_at(2), "->", lst.to_list())
    print("lst.remove_at(0) =", lst.remove_at(0), "->", lst.to_list())
    print("lst.remove_at(2) =", lst.remove_at(2), "->", lst.to_list())
    print(f"Длина: {len(lst)}, tail = {lst.tail.value if lst.tail else None}")

    print("\n--- Очередь на списке ---")
    q = ListQueue()
    for v in ["заявка-1", "заявка-2", "заявка-3"]:
        q.enqueue(v)
    print("Очередь:", q.to_list())
    print("dequeue ->", q.dequeue(), "| осталось:", q.to_list())
    print("dequeue ->", q.dequeue(), "| осталось:", q.to_list())

    print("\n--- Журнал операций (прикладная задача) ---")
    j = OperationJournal()
    for op in ["create client-1", "update client-1",
               "create client-2", "update client-2", "delete client-1"]:
        j.append(op)
    print("Журнал:", j)
    print("get(2) =", j.get(2))
    print("delete(2) ->", j.delete(2), "| журнал:", j)
    print("cancel_last() ->", j.cancel_last(), "| журнал:", j)

    # ---------- Т2: замеры ----------
    SIZES = [1000, 2000, 4000]
    print(f"\n{'n':>6} {'LL доступ':>14} {'list доступ':>14}"
          f" {'LL удаление':>15} {'list удаление':>16}")

    results = {"ll_get": [], "py_get": [], "ll_remove": [], "py_remove": []}
    for n in SIZES:
        ll = LinkedList()
        for i in range(n):
            ll.push_back(i)
        py = list(range(n))

        # Доступ по индексу: ~200 обращений, равномерно по массиву
        step = max(1, n // 200)

        def ll_get():
            for i in range(0, n, step):
                ll.get(i)

        def py_get():
            for i in range(0, n, step):
                py[i]

        # Удаление из середины: 100 удалений из середины.
        # После каждого удаления восстанавливаем длину (push_back),
        # чтобы n не «таял» и замеры были сопоставимы.
        def ll_remove():
            for _ in range(100):
                ll.remove_at(n // 2)
                ll.push_back(0)

        def py_remove():
            for _ in range(100):
                py.pop(n // 2)
                py.append(0)

        t_ll_get = measure(ll_get)
        t_py_get = measure(py_get)
        t_ll_rm = measure(ll_remove)
        t_py_rm = measure(py_remove)

        results["ll_get"].append(t_ll_get)
        results["py_get"].append(t_py_get)
        results["ll_remove"].append(t_ll_rm)
        results["py_remove"].append(t_py_rm)
        print(f"{n:>6}{t_ll_get:>14.6f}{t_py_get:>14.6f}"
              f"{t_ll_rm:>15.6f}{t_py_rm:>16.6f}")

    # ---------- Т4: расход памяти ----------
    print("\n--- Т4: расход памяти на 10 000 элементов, байт ---")
    N_MEM = 10_000
    ll = LinkedList()
    for i in range(N_MEM):
        ll.push_back(i)
    py = list(range(N_MEM))

    # Оцениваем размер одного узла: сам Node + int + поле next (8 байт)
    node_size = sys.getsizeof(Node(0)) + sys.getsizeof(0) + 8
    print(f"LinkedList: ~{N_MEM * node_size} байт "
          f"({node_size} байт/узел, оценка)")
    print(f"list:       ~{sys.getsizeof(py)} байт "
          f"({sys.getsizeof(py) / N_MEM:.2f} байт/элемент)")

    # ---------- Графики ----------
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(SIZES, results["ll_get"], "o-", label="LL get(i)")
    axes[0].plot(SIZES, results["py_get"], "s-", label="list[i]")
    axes[0].set_xlabel("n")
    axes[0].set_ylabel("Время, с")
    axes[0].set_title("Доступ по индексу (~200 запросов)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(SIZES, results["ll_remove"], "o-", label="LL remove_at(n/2)")
    axes[1].plot(SIZES, results["py_remove"], "s-", label="list.pop(n/2)")
    axes[1].set_xlabel("n")
    axes[1].set_ylabel("Время, с")
    axes[1].set_title("Удаление из середины (100 удалений)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig("lr6_plot.png", dpi=150)
    plt.show()