from datetime import datetime
from typing import Any, Callable, List, Optional, Protocol, Sequence

from pydantic import BaseModel, Field, PrivateAttr, model_validator
from typing_extensions import Literal


class Recurrence(Protocol):

    # def take(self, n: int) -> Sequence[datetime]: ...

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
    last_run: datetime | None = None
    next_run: datetime | None = None
    past_events: pasteventtype = Field(default="lastonly")

    @model_validator(mode="before")
    def set_last_run(cls, values: dict[str, Any]) -> dict[str, Any]:

        allow_infinite = values.get("allow_infinite")
        count = values.get("count")
        until = values.get("until")
        if not allow_infinite and count is None and until is None:
            raise ValueError(
                "If 'allow_infinite' = False, A 'count' or 'until' should be set."
            )

        # last_run = values.get("last_run")
        # dtstart = values.get("dtstart")
        # if last_run is None and dtstart is not None:
        # values["last_run"] = dtstart

        return values


recurrenceFactory = Callable[[RecurrenceConfig], Recurrence]


class SchedulerManager(BaseModel):
    _recur: Recurrence = PrivateAttr()
    config: RecurrenceConfig

    def inject_recur(self, recur: Recurrence):
        self._recur = recur
        self.config.last_run = self.config.last_run or self.config.dtstart
        if self.next_run is None:
            # the type ignored below is guaranteed by pydantic (dtstart can´t ne None)
            self._update_next(self.last_run)  # type: ignore

    @property
    def count(self) -> int | None:
        return self.config.count

    @property
    def last_run(self) -> datetime:
        return self.config.last_run  # type: ignore

    @property
    def next_run(self) -> datetime | None:
        return self.config.next_run

    def _filtdates(self, dates: List[datetime]) -> List[datetime]:
        if self.config.past_events == "none":
            return []
        if self.config.past_events == "all":
            return dates
        return dates[-1:]

    def is_exhausted(self, dt: datetime) -> bool:
        if self.config.count is not None and self.config.count <= 0:
            return True
        if self.config.until and dt > self.config.until:
            return True
        return False

    def _update_next(self, dt: datetime) -> None:

        nr = self._recur.after(dt)
        if nr is not None and not self.is_exhausted(nr):
            if self.next_run is None or nr > self.next_run:
                self.config.next_run = nr
        else:
            self.config.next_run = None

    def schedule(self, until: datetime) -> list[datetime]:

        # last_run = self.config.last_run or self.config.dtstart
        dates = self._recur.between(self.last_run, until, inc=True)

        if self.config.count is not None:
            self.config.count = max(0, self.config.count - len(dates))

        self.config.last_run = dates[-1] if dates else self.last_run
        if dates:
            self._update_next(dates[-1])

        return self._filtdates(dates)


def make_scheduler(
    make_recurrence: recurrenceFactory, config: RecurrenceConfig
) -> SchedulerManager:
    recur = make_recurrence(config)

    schmngr = SchedulerManager(config=config)
    schmngr.inject_recur(recur)

    return schmngr
