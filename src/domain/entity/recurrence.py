from datetime import datetime
from logging import config
from typing import (
    Callable,
    Iterator,
    List,
    Optional,
    Protocol,
    Sequence,
    runtime_checkable,
)

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Literal

from domain.vo.weekdays import WeekdayStr


class Recurrence(Protocol):

    def __iter__(self) -> Iterator[datetime]: ...

    def take(self, n: int) -> Sequence[datetime]: ...

    def after(self, dt: datetime, inclusive: bool = False) -> datetime | None: ...

    def between(
        self, dtstart: datetime, until: datetime, inc: bool = False
    ) -> list[datetime]: ...


class RecurrenceConfig(BaseModel):
    freq: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
    dtstart: datetime
    interval: int = 1
    count: int | None = None
    until: datetime | None = None
    byweekday: list[WeekdayStr] | None = None
    bymonthday: list[int] | None = None
    allow_infinite: bool = False
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    past_events: Literal["all", "lastonly", "none"] = Field(default="lastonly")

    @model_validator(mode="after")
    def check_count_or_until(self) -> "RecurrenceConfig":
        if not self.allow_infinite and self.count is None and self.until is None:
            raise ValueError("Você deve definir pelo menos 'count' ou 'until'")
        return self


@runtime_checkable
class SchedulerProtocol(Protocol):

    def is_exhausted(self, final: datetime) -> bool: ...

    def schedule(self, until: datetime) -> list[datetime]: ...

    @property
    def count(self) -> int: ...
    @property
    def last_run(self) -> datetime | None: ...
    @property
    def next_run(self) -> datetime | None: ...


recurrenceFactory = Callable[[RecurrenceConfig], Recurrence]

SchedulerFactory = Callable[[RecurrenceConfig], SchedulerProtocol]


class SchedulerManager(BaseModel):
    factory: recurrenceFactory
    config: RecurrenceConfig

    @property
    def count(self) -> int | None:
        return self.config.count

    @property
    def last_run(self) -> datetime | None:
        return self.config.last_run

    @property
    def next_run(self) -> datetime | None:
        return self.config.next_run

    def _filtdates(self, dates: List[datetime]) -> List[datetime]:
        if self.config.past_events == "none":
            return []
        if self.config.past_events == "all":
            return dates
        return dates[-1:]

    def is_exhausted(self, final: datetime) -> bool:
        if self.config.count is not None and self.config.count == 0:
            return True
        if self.config.until and self.config.until < final:
            return True
        return False

    def _update_next(self, recur: Recurrence, dt: datetime):
        nr = recur.after(dt)
        if nr is not None:
            if self.next_run is None or nr < self.next_run:
                self.config.next_run = nr

    def schedule(self, until: datetime) -> list[datetime]:

        recur = self.factory(self.config)
        last_run = self.config.last_run or self.config.dtstart
        dates = recur.between(last_run, until)

        if self.config.count is not None:
            self.config.count = max(0, self.config.count - len(dates))

        self.config.last_run = dates[-1] if dates else last_run
        if dates:
            self._update_next(recur, dates[-1])

        return self._filtdates(dates)
