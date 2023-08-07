from bisect import bisect_left
from datetime import datetime
from time import monotonic
from typing import Any, Generic, Hashable, OrderedDict, TypeVar

from pydantic import BaseModel


class DataModel(BaseModel, arbitrary_types_allowed=True):
    pass


T = TypeVar('T')
KT = TypeVar('KT')
Seconds = int


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


class TimeAwareCounter(Generic[T]):
    def __init__(self, period: Seconds, name: str = "") -> None:
        self.period = period
        self.last_timestamp = None
        self.counter = 0
        self._timestamps = []

    @property
    def timestamps(self) -> list[tuple[int, T]]:
        now = datetime.now().timestamp()
        last_allowed_timestamp = now - self.period
        if self._timestamps and self._timestamps[0][0] <= last_allowed_timestamp:
            last_allowed_timestamp_index = bisect_left(
                self._timestamps, last_allowed_timestamp, key=lambda i: i[0]
            )
            self._timestamps = self._timestamps[last_allowed_timestamp_index:]
        return self._timestamps

    def inc(self):
        self.add(None)

    def add(self, value: Hashable):
        self.timestamps.append((datetime.now().timestamp(), value))

    def count(self):
        return len(self.timestamps)

    def count_unique(self):
        return len({v for _, v in self.timestamps})
