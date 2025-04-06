from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Sequence

from dateutil.rrule import DAILY, FR, MO, MONTHLY, SA, SU, TH, TU, WE, WEEKLY, YEARLY
from dateutil.rrule import rrule as RRuleType

from domain.entity.recurrence import Recurrence, RecurrenceConfig


@dataclass
class RRuleRecurrence(Recurrence):
    _rule: RRuleType

    def __iter__(self) -> Iterator[datetime]:
        return iter(self._rule)

    def take(self, n: int) -> Sequence[datetime]:
        return [dt for _, dt in zip(range(n), self._rule)]

    def after(self, dt: datetime, inclusive: bool = False) -> datetime | None:
        return self._rule.after(dt, inc=inclusive)  # type: ignore

    def between(
        self, dtstart: datetime, until: datetime, inc: bool = False
    ) -> list[datetime]:
        return list(self._rule.between(dtstart, until, inc=inc))  # type: ignore


def rrule_factory(config: RecurrenceConfig) -> Recurrence:
    freq_map = {
        "DAILY": DAILY,
        "WEEKLY": WEEKLY,
        "MONTHLY": MONTHLY,
        "YEARLY": YEARLY,
    }
    WEEKDAYS = {"MO": MO, "TU": TU, "WE": WE, "TH": TH, "FR": FR, "SA": SA, "SU": SU}

    rule = RRuleType(
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

    config = RecurrenceConfig(
        freq="DAILY",
        dtstart=datetime(2023, 10, 1),
        interval=1,
        count=5,
        byweekday=["MO", "WE", "FR"],
    )
    recurrence = rrule_factory(config)

    for date in recurrence.take(5):
        print(date)

    cfg = RecurrenceConfig(
        freq="WEEKLY",
        dtstart=datetime(2025, 4, 5),
        interval=1,
        byweekday=["MO", "FR"],
        count=4,
    )

    rec = rrule_factory(cfg)
    print(rec.take(3))
    # [2025-04-07, 2025-04-11, 2025-04-14]
