from time import monotonic
from typing import Any, Hashable, Iterable, Iterator, Mapping, TypeVar

from pydantic import BaseModel


class DataModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


T = TypeVar('T')
KT = TypeVar('KT')


class InverseMapping(Mapping[KT, T]):
    """
    Returns given value if key not in declared keys, raises KeyError otherwise
    """

    __slots__ = ('_keys', '_value')

    def __init__(self, keys: Iterable[KT], value: T, /):
        self._keys = set(keys)
        self._value = value

    def __len__(self) -> int:
        return len(self._keys)

    def __getitem__(self, k: Hashable) -> T:
        if k in self._keys:
            raise KeyError(f'Key {k!r} found in {self}')
        return self._value

    def __contains__(self, k: Hashable) -> bool:  # type: ignore
        return k not in self._keys

    def __iter__(self) -> Iterator[KT]:
        yield from self._keys

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._keys}, {self._value})'


class Timer:
    __slots__ = 'name', 'elapsed', '_start_time'

    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self: T) -> T:
        self._start_time = monotonic()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed = monotonic() - self._start_time

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}({self.name!r}, elapsed={getattr(self, "elapsed", "...")})'
        )
