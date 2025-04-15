from datetime import datetime
from typing import Any

import pytest

from domain.entity.recurrence import RecurrenceConfig, make_scheduler
from infra.recurrence.rruleadaptor import rrule_factory


def make_cfg(**kwargs: Any) -> RecurrenceConfig:
    """Utilitário para criar configs rápidas."""
    base = dict(
        freq="DAILY",
        dtstart=datetime(2025, 4, 15),
        interval=1,
        allow_infinite=True,
    )
    base.update(kwargs)
    return RecurrenceConfig(**base)


def test_daily_recurrence_all_dates():
    cfg = make_cfg(past_events="all")
    sched = make_scheduler(rrule_factory, cfg)

    dates = sched.schedule(datetime(2025, 4, 18))

    assert len(dates) == 4  # 15, 16, 17, 18
    assert dates[0] == datetime(2025, 4, 15)
    assert dates[-1] == datetime(2025, 4, 18)


def test_daily_every_two_days():
    cfg = make_cfg(interval=2, past_events="all")
    sched = make_scheduler(rrule_factory, cfg)

    dates = sched.schedule(datetime(2025, 4, 21))

    assert dates == [
        datetime(2025, 4, 15),
        datetime(2025, 4, 17),
        datetime(2025, 4, 19),
        datetime(2025, 4, 21),
    ]


def test_count_one_returns_one():
    cfg = make_cfg(count=1, past_events="all")
    sched = make_scheduler(rrule_factory, cfg)

    dates = sched.schedule(datetime(2025, 4, 20))
    assert len(dates) == 1
    assert dates[0] == datetime(2025, 4, 15)
    assert sched.is_exhausted(datetime(2025, 4, 16)) is True


def test_past_events_none_returns_empty():
    cfg = make_cfg(past_events="none")
    sched = make_scheduler(rrule_factory, cfg)

    dates = sched.schedule(datetime(2025, 4, 20))
    assert dates == []


def test_past_events_lastonly_returns_last():
    cfg = make_cfg(past_events="lastonly")
    sched = make_scheduler(rrule_factory, cfg)

    dates = sched.schedule(datetime(2025, 4, 20))
    assert len(dates) == 1
    assert dates[0] == datetime(2025, 4, 20)


def test_next_run_updates_properly():
    cfg = make_cfg(past_events="lastonly")
    sched = make_scheduler(rrule_factory, cfg)

    _ = sched.schedule(datetime(2025, 4, 20))
    assert sched.next_run == datetime(2025, 4, 21)


def test_scheduler_respects_until():
    cfg = make_cfg(until=datetime(2025, 4, 17), past_events="all")
    sched = make_scheduler(rrule_factory, cfg)

    dates = sched.schedule(datetime(2025, 4, 30))
    assert dates == [
        datetime(2025, 4, 15),
        datetime(2025, 4, 16),
        datetime(2025, 4, 17),
    ]
    assert sched.is_exhausted(datetime(2025, 4, 18))


def test_weekday_filtering():
    cfg = make_cfg(
        freq="WEEKLY",
        byweekday=["MO", "WE", "FR"],
        dtstart=datetime(2025, 4, 14),
        past_events="all",
    )
    sched = make_scheduler(rrule_factory, cfg)
    dates = sched.schedule(datetime(2025, 4, 21))

    assert dates == [
        datetime(2025, 4, 14),  # Monday
        datetime(2025, 4, 16),  # Wednesday
        datetime(2025, 4, 18),  # Friday
        datetime(2025, 4, 21),  # Monday
    ]
