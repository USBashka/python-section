from dataclasses import dataclass, field
from itertools import batched
from typing import Iterable, TypeAlias, Iterator

SomeRemoteData: TypeAlias = int


@dataclass
class Query:
    per_page: int = 3
    page: int = 1


@dataclass
class Page:
    per_page: int = 3
    results: Iterable[SomeRemoteData] = field(default_factory=list)
    next: int | None = None


def request(query: Query) -> Page:
    data = [i for i in range(0, 10)]
    chunks = list(batched(data, query.per_page))
    return Page(
        per_page=query.per_page,
        results=chunks[query.page - 1],
        next=query.page + 1 if query.page < len(chunks) else None,
    )


class RetrieveRemoteData:
    """Класс-генератор постраничной выборки из API"""
    def __init__(self, per_page: int = 3):
        self.per_page = per_page

    def __iter__(self) -> Iterator[SomeRemoteData]:
        def gen() -> Iterator[SomeRemoteData]:
            page_num = 1
            while True:
                page = request(Query(per_page=self.per_page, page=page_num))
                for item in page.results:
                    yield item
                if page.next is None:
                    break
                page_num = page.next
        return gen()


class Fibo:
    """Итератор последовательности Фибоначчи от 0 длиной n"""
    def __init__(self, n: int):
        if not isinstance(n, int) or n < 0:
            raise ValueError("N must be a non-negative integer")
        self.n = n
        self._i = 0
        self._a = 0
        self._b = 1

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._i >= self.n:
            raise StopIteration
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        self._i += 1
        return value



def main():
    print(list(Fibo(10)))
    print(list(RetrieveRemoteData(per_page=3)))


if __name__ == "__main__":
    main()