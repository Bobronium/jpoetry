from time import monotonic
from typing import Any, TypeVar

from pydantic import BaseModel


class DataModel(BaseModel, arbitrary_types_allowed=True):
    pass


T = TypeVar('T')
KT = TypeVar('KT')


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
        return f'{self.__class__.__name__}({self.name!r}, elapsed={getattr(self, "elapsed", "...")})'
