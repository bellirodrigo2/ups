from datetime import datetime
from typing import Callable, List, Optional, Protocol, Sequence

from pydantic import BaseModel, Field, PrivateAttr, model_validator
from typing_extensions import Literal


class Recurrence(Protocol):

    def take(self, n: int) -> Sequence[datetime]: ...

    def after(self, dt: datetime, inclusive: bool = False) -> datetime | None: ...

    def between(
        self, dtstart: datetime, until: datetime, inc: bool = False
    ) -> list[datetime]: ...


freqtype = Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]

weekdaytype = Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

pasteventtype = Literal["all", "lastonly", "none"]


class RecurrenceConfig(BaseModel):
    freq: freqtype
    dtstart: datetime
    interval: int = 1
    count: int | None = None
    until: datetime | None = None
    byweekday: list[weekdaytype] | None = None
    bymonthday: list[int] | None = None
    allow_infinite: bool = False
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    past_events: pasteventtype = Field(default="lastonly")

    @model_validator(mode="after")
    def check_count_or_until(self) -> "RecurrenceConfig":
        if not self.allow_infinite and self.count is None and self.until is None:
            raise ValueError("Você deve definir pelo menos 'count' ou 'until'")
        return self


recurrenceFactory = Callable[[RecurrenceConfig], Recurrence]


class SchedulerManager(BaseModel):
    _recur: Recurrence = PrivateAttr()
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

    def _update_next(self, dt: datetime):
        nr = self._recur.after(dt)
        if nr is not None:
            if self.next_run is None or nr < self.next_run:
                self.config.next_run = nr

    def schedule(self, until: datetime) -> list[datetime]:

        last_run = self.config.last_run or self.config.dtstart
        dates = self._recur.between(last_run, until)

        if self.config.count is not None:
            self.config.count = max(0, self.config.count - len(dates))

        self.config.last_run = dates[-1] if dates else last_run
        if dates:
            self._update_next(dates[-1])

        return self._filtdates(dates)


def make_scheduler(
    make_recurrence: recurrenceFactory, config: RecurrenceConfig
) -> SchedulerManager:
    recur = make_recurrence(config)

    return SchedulerManager(_recur=recur, config=config)
