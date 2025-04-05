from datetime import datetime
from typing import Callable, Iterator, Literal, Protocol, Sequence

from pydantic import BaseModel, model_validator


class Recurrence(Protocol):

    def __iter__(self) -> Iterator[datetime]: ...

    def take(self, n: int) -> Sequence[datetime]: ...

    def after(self, dt: datetime, inclusive: bool = False) -> datetime | None: ...

    def between(
        self, dtstart: datetime, until: datetime, inc: bool = False
    ) -> list[datetime]: ...


WeekdayStr = Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


class RecurrenceConfig(BaseModel):
    freq: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
    dtstart: datetime
    interval: int = 1
    count: int | None = None
    until: datetime | None = None
    byweekday: list[WeekdayStr] | None = None
    bymonthday: list[int] | None = None
    allow_infinite: bool = False

    @model_validator(mode="after")
    def check_count_or_until(self) -> "RecurrenceConfig":
        if not self.allow_infinite and self.count is None and self.until is None:
            raise ValueError("Você deve definir pelo menos 'count' ou 'until'")
        return self


recurrenceFactory = Callable[[RecurrenceConfig], Recurrence]
