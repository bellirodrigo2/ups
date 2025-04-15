from dataclasses import dataclass
from datetime import datetime, tzinfo
from typing import Protocol

import pendulum


class TimeZoneProvider(Protocol):
    def normalize(self, dt: datetime, target_tz: tzinfo) -> datetime: ...
    def get_timezone_name(self, tz: tzinfo) -> str: ...
    def get_utc_timezone(self) -> tzinfo: ...


class DateTimeProviderProtocol(Protocol):
    def now(self, tz: tzinfo | None = None) -> datetime: ...
    def normalize(self, dt: datetime, target_tz: tzinfo | None = None) -> datetime: ...


@dataclass
class DateTimeProvider:
    time_zone_provider: TimeZoneProvider

    def now(self, tz: tzinfo | None = None) -> datetime:
        tz = tz or self.time_zone_provider.get_utc_timezone()
        return datetime.now(tz)

    def normalize(self, dt: datetime, target_tz: tzinfo | None = None) -> datetime:
        target_tz = target_tz or self.time_zone_provider.get_utc_timezone()
        return self.time_zone_provider.normalize(dt, target_tz)


@dataclass
class PendulumTimeZoneProvider:
    def normalize(self, dt: datetime, target_tz: tzinfo) -> datetime:
        pdt = pendulum.instance(dt)
        return pdt.in_timezone(self.get_timezone_name(target_tz))

    def get_timezone_name(self, tz: tzinfo) -> str:
        zone = getattr(tz, "zone", None)
        if not isinstance(zone, str):
            raise ValueError("tzinfo does not have a string 'zone' attribute")
        return zone

    def get_utc_timezone(self) -> tzinfo:
        return pendulum.timezone("UTC")


from dataclasses import dataclass
from datetime import datetime, tzinfo

from dateutil import tz as dateutil_tz


@dataclass
class DateutilTimeZoneProvider:
    def normalize(self, dt: datetime, target_tz: tzinfo) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=self.get_utc_timezone())
        return dt.astimezone(target_tz)

    def get_timezone_name(self, tz: tzinfo) -> str:
        zone = getattr(tz, "zone", None)
        if not isinstance(zone, str):
            raise ValueError("tzinfo does not have a string 'zone' attribute")
        return zone

    def get_utc_timezone(self) -> tzinfo:
        return dateutil_tz.tzutc()
