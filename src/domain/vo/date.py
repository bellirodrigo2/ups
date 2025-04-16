import inspect
from datetime import datetime, timedelta
from typing import Any, Protocol, Tuple, Union, runtime_checkable

from dateutil.relativedelta import relativedelta


@runtime_checkable
class Itimedelta(Protocol):
    @property
    def days(self) -> int: ...
    @property
    def seconds(self) -> int: ...
    @property
    def microseconds(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def total_seconds(self) -> float: ...
    def __add__(
        self, other: Union["Itimedelta", datetime]
    ) -> Union["Itimedelta", datetime]: ...
    def __radd__(
        self, other: Union["Itimedelta", datetime]
    ) -> Union["Itimedelta", datetime]: ...
    def __sub__(
        self, other: Union["Itimedelta", datetime]
    ) -> Union["Itimedelta", datetime]: ...
    def __rsub__(
        self, other: Union["Itimedelta", datetime]
    ) -> Union["Itimedelta", datetime]: ...
    def __neg__(self) -> "Itimedelta": ...
    def __pos__(self) -> "Itimedelta": ...
    def __abs__(self) -> "Itimedelta": ...
    def __mul__(self, other: Union[int, float]) -> "Itimedelta": ...
    def __rmul__(self, other: Union[int, float]) -> "Itimedelta": ...
    def __floordiv__(
        self, other: Union[int, "Itimedelta"]
    ) -> Union[int, "Itimedelta"]: ...
    def __truediv__(
        self, other: Union[int, float, "Itimedelta"]
    ) -> Union[float, "Itimedelta"]: ...
    def __mod__(self, other: "Itimedelta") -> "Itimedelta": ...
    def __divmod__(self, other: "Itimedelta") -> Tuple[int, "Itimedelta"]: ...
    def __eq__(self, other: object) -> bool: ...
    def __lt__(self, other: "Itimedelta") -> bool: ...
    def __le__(self, other: "Itimedelta") -> bool: ...
    def __gt__(self, other: "Itimedelta") -> bool: ...
    def __ge__(self, other: "Itimedelta") -> bool: ...
    def __hash__(self) -> int: ...
    def __bool__(self) -> bool: ...
    def __reduce__(self) -> Tuple[Any, ...]: ...


class Flextimedelta(Itimedelta):
    def __init__(
        self,
        days: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
        months: int = 0,
        years: int = 0,
        **kwargs: Any,
    ) -> None:
        # Interno: usa timedelta para dias/segundos/microseconds
        self._timedelta = timedelta(
            days=days, seconds=seconds, microseconds=microseconds, **kwargs
        )
        self.months = months
        self.years = years

    def __repr__(self) -> str:
        return (
            f"Flextimedelta(days={self._timedelta.days}, seconds={self._timedelta.seconds}, "
            f"microseconds={self._timedelta.microseconds}, months={self.months}, years={self.years})"
        )

    def __str__(self) -> str:
        return f"Flextimedelta({self._timedelta}, months={self.months}, years={self.years})"

    def __add__(
        self,
        other: Union[datetime, timedelta, "Flextimedelta"],
    ) -> Union[datetime, timedelta, "Flextimedelta"]:
        # Flextimedelta + Flextimedelta
        if isinstance(other, Flextimedelta):
            return Flextimedelta(
                days=self._timedelta.days + other._timedelta.days,
                seconds=self._timedelta.seconds + other._timedelta.seconds,
                microseconds=self._timedelta.microseconds
                + other._timedelta.microseconds,
                months=self.months + other.months,
                years=self.years + other.years,
            )
        # Flextimedelta + datetime
        if isinstance(other, datetime):
            delta = relativedelta(years=self.years, months=self.months)
            return other + delta + self._timedelta
        # Flextimedelta + timedelta
        if isinstance(other, timedelta):
            td = self._timedelta + other
            return Flextimedelta(
                days=td.days,
                seconds=td.seconds,
                microseconds=td.microseconds,
                months=self.months,
                years=self.years,
            )
        return NotImplemented

    def __radd__(
        self,
        other: Union[datetime, timedelta],
    ) -> Union[datetime, timedelta]:
        return self.__add__(other)

    def __sub__(
        self,
        other: Union[datetime, timedelta, "Flextimedelta"],
    ) -> Union[datetime, timedelta, "Flextimedelta"]:
        # Flextimedelta - Flextimedelta
        if isinstance(other, Flextimedelta):
            return Flextimedelta(
                days=self._timedelta.days - other._timedelta.days,
                seconds=self._timedelta.seconds - other._timedelta.seconds,
                microseconds=self._timedelta.microseconds
                - other._timedelta.microseconds,
                months=self.months - other.months,
                years=self.years - other.years,
            )
        # datetime - Flextimedelta
        if isinstance(other, datetime):
            delta = relativedelta(years=self.years, months=self.months)
            return other - delta - self._timedelta
        # Flextimedelta - timedelta
        if isinstance(other, timedelta):
            td = self._timedelta - other
            return Flextimedelta(
                days=td.days,
                seconds=td.seconds,
                microseconds=td.microseconds,
                months=self.months,
                years=self.years,
            )
        return NotImplemented

    def __rsub__(
        self,
        other: Union[datetime, timedelta],
    ) -> Union[datetime, timedelta]:
        # datetime - Flextimedelta
        if isinstance(other, datetime):
            return self.__sub__(other)
        # timedelta - Flextimedelta
        if isinstance(other, timedelta):
            td = other - self._timedelta
            return Flextimedelta(
                days=td.days,
                seconds=td.seconds,
                microseconds=td.microseconds,
                months=-self.months,
                years=-self.years,
            )
        return NotImplemented

    def __neg__(self) -> "Flextimedelta":
        return Flextimedelta(
            days=-self._timedelta.days,
            seconds=-self._timedelta.seconds,
            microseconds=-self._timedelta.microseconds,
            months=-self.months,
            years=-self.years,
        )

    def __pos__(self) -> "Flextimedelta":
        return self

    def __abs__(self) -> "Flextimedelta":
        return Flextimedelta(
            days=abs(self._timedelta.days),
            seconds=abs(self._timedelta.seconds),
            microseconds=abs(self._timedelta.microseconds),
            months=abs(self.months),
            years=abs(self.years),
        )

    def __mul__(
        self,
        other: Union[int, float],
    ) -> "Flextimedelta":
        return Flextimedelta(
            days=self._timedelta.days * other,
            seconds=self._timedelta.seconds * other,
            microseconds=self._timedelta.microseconds * other,
            months=self.months * other,
            years=self.years * other,
        )

    __rmul__ = __mul__

    def __floordiv__(
        self,
        other: Union[int, "Flextimedelta"],
    ) -> Union[int, "Flextimedelta"]:
        if isinstance(other, Flextimedelta):
            return self.days // other.days
        if isinstance(other, int):
            return Flextimedelta(
                days=self._timedelta.days // other,
                seconds=self._timedelta.seconds // other,
                microseconds=self._timedelta.microseconds // other,
                months=self.months // other,
                years=self.years // other,
            )
        return NotImplemented

    def __truediv__(
        self,
        other: Union[int, float, "Flextimedelta"],
    ) -> Union[float, "Flextimedelta"]:
        if isinstance(other, Flextimedelta):
            return self.total_seconds() / other.total_seconds()
        if isinstance(other, (int, float)):
            return Flextimedelta(
                days=self._timedelta.days / other,
                seconds=self._timedelta.seconds / other,
                microseconds=self._timedelta.microseconds / other,
                months=self.months / other,
                years=self.years / other,
            )
        return NotImplemented

    def __mod__(
        self,
        other: Union["Flextimedelta", int],
    ) -> int:
        if isinstance(other, Flextimedelta):
            return self.days % other.days
        if isinstance(other, int):
            return self.days % other
        return NotImplemented

    def __divmod__(self, other: "Flextimedelta") -> Tuple[int, "Flextimedelta"]:
        if isinstance(other, Flextimedelta):
            q = int(self.total_seconds() // other.total_seconds())
            r_secs = self.total_seconds() % other.total_seconds()
            r = Flextimedelta(seconds=r_secs)
            return q, r
        return NotImplemented

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(other, Flextimedelta):
            return False
        return (
            self._timedelta == other._timedelta
            and self.months == other.months
            and self.years == other.years
        )

    def __ne__(
        self,
        other: object,
    ) -> bool:
        return not self == other

    def __lt__(self, other: Union["Flextimedelta", timedelta]) -> bool:
        if isinstance(other, Flextimedelta):
            return self.total_seconds() < other.total_seconds()
        elif isinstance(other, timedelta):
            # If the other object is a timedelta, compare it using total_seconds
            return self.total_seconds() < other.total_seconds()
        return NotImplemented

    def __le__(
        self,
        other: Union["Flextimedelta", timedelta],
    ) -> bool:
        return self.total_seconds() <= other.total_seconds()

    def __gt__(
        self,
        other: Union["Flextimedelta", timedelta],
    ) -> bool:
        return self.total_seconds() > other.total_seconds()

    def __ge__(
        self,
        other: Union["Flextimedelta", timedelta],
    ) -> bool:
        return self.total_seconds() >= other.total_seconds()

    def total_seconds(self) -> float:
        base_seconds = self._timedelta.total_seconds()
        additional_seconds = (self.years * 365.25 + self.months * 30.44) * 86400
        return base_seconds + additional_seconds

    def to_relativedelta(self) -> relativedelta:
        return relativedelta(
            years=self.years,
            months=self.months,
            days=self._timedelta.days,
            seconds=self._timedelta.seconds,
            microseconds=self._timedelta.microseconds,
        )

    @property
    def days(self) -> int:
        return self._timedelta.days

    @property
    def seconds(self) -> int:
        return self._timedelta.seconds

    @property
    def microseconds(self) -> int:
        return self._timedelta.microseconds

    def __hash__(self) -> int:
        return hash(
            (
                self.days,
                self.seconds,
                self.microseconds,
                self.months,
                self.years,
            )
        )

    def __reduce__(self) -> Tuple[Any, ...]:
        return (
            self.__class__,
            (self.days, self.seconds, self.microseconds, self.months, self.years),
        )

    def __bool__(self) -> bool:
        return bool(self._timedelta) or self.months != 0 or self.years != 0


def _make_timedelta(v: int) -> Itimedelta:
    caller = inspect.stack()[1].function
    return Flextimedelta(**{caller: v})


def days(v: int) -> Itimedelta:
    return _make_timedelta(v)


def minutes(v: int) -> Itimedelta:
    return _make_timedelta(v)


def hours(v: int) -> Itimedelta:
    return _make_timedelta(v)


def months(v: int) -> Itimedelta:
    return _make_timedelta(v)


def years(v: int) -> Itimedelta:
    return _make_timedelta(v)
