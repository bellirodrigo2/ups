from datetime import datetime
from typing import Iterator, Literal, Optional, Protocol, Sequence

from dateutil.rrule import rrule
from pydantic import BaseModel, model_validator


class Recurrence(Protocol):

    def __iter__(self) -> Iterator[datetime]: ...

    def take(self, n: int) -> Sequence[datetime]: ...

    def after(self, dt: datetime, inclusive: bool = False) -> datetime | None: ...

    def between(
        self, dtstart: datetime, until: datetime, inc: bool = False
    ) -> list[datetime]: ...


class RRuleRecurrence(BaseModel):
    _rule: rrule

    def __iter__(self) -> Iterator[datetime]:
        return iter(self._rule)

    def take(self, n: int) -> Sequence[datetime]:
        return [dt for _, dt in zip(range(n), self._rule)]

    def after(self, dt: datetime, inclusive: bool = False) -> datetime | None:
        return self._rule.after(dt, inc=inclusive)

    def between(
        self, dtstart: datetime, until: datetime, inc: bool = False
    ) -> list[datetime]:
        return list(self._rule.between(dtstart, until, inc=inc))


from dateutil.rrule import (
    DAILY,
    FR,
    MO,
    MONTHLY,
    SA,
    SU,
    TH,
    TU,
    WE,
    WEEKLY,
    YEARLY,
    rrule,
)

WeekdayStr = Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

WEEKDAYS = {"MO": MO, "TU": TU, "WE": WE, "TH": TH, "FR": FR, "SA": SA, "SU": SU}


class RecurrenceRuleConfig(BaseModel):
    freq: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
    dtstart: datetime
    interval: int = 1
    count: int | None = None
    until: datetime | None = None
    byweekday: list[WeekdayStr] | None = None
    bymonthday: list[int] | None = None
    allow_infinite: bool = False

    @model_validator(mode="after")
    def check_count_or_until(self) -> "RecurrenceRuleConfig":
        if not self.allow_infinite and self.count is None and self.until is None:
            raise ValueError("Você deve definir pelo menos 'count' ou 'until'")
        return self


class RecurrenceFactory:
    @staticmethod
    def create(config: RecurrenceRuleConfig) -> Recurrence:
        freq_map = {
            "DAILY": DAILY,
            "WEEKLY": WEEKLY,
            "MONTHLY": MONTHLY,
            "YEARLY": YEARLY,
        }

        rule = rrule(
            freq=freq_map[config.freq],
            dtstart=config.dtstart,
            interval=config.interval,
            count=config.count,
            until=config.until,
            byweekday=(
                [WEEKDAYS[d] for d in config.byweekday] if config.byweekday else None
            ),
            bymonthday=config.bymonthday,
        )

        return RRuleRecurrence(_rule=rule)


if __name__ == "__main__":

    config = RecurrenceRuleConfig(
        freq="DAILY",
        dtstart=datetime(2023, 10, 1),
        interval=1,
        count=5,
        byweekday=["MO", "WE", "FR"],
    )
    recurrence = RecurrenceFactory.create(config)

    for date in recurrence.take(5):
        print(date)

    cfg = RecurrenceRuleConfig(
        freq="WEEKLY",
        dtstart=datetime(2025, 4, 5),
        interval=1,
        byweekday=["MO", "FR"],
        count=4,
    )

    rec = RecurrenceFactory.create(cfg)
    print(rec.take(3))
    # [2025-04-07, 2025-04-11, 2025-04-14]
