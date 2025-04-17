import inspect
import warnings
from dataclasses import dataclass
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


from datetime import datetime, timedelta
from typing import Any, Protocol, Tuple, Union, runtime_checkable

from dateutil.relativedelta import relativedelta


def timedelta_ext(
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    months: int = 0,
    years: int = 0,
) -> Itimedelta:
    td = timedelta(days=days, seconds=seconds, microseconds=microseconds)
    rd = relativedelta(months=months, years=years)
    return Flextimedelta(_td=td, _rd=rd)


@dataclass
class Flextimedelta(Itimedelta):
    _td: timedelta
    _rd: relativedelta

    @property
    def days(self):
        return self._td.days

    @property
    def seconds(self):
        return self._td.seconds

    @property
    def microseconds(self):
        return self._td.microseconds

    @property
    def months(self):
        return self._rd.months

    @property
    def years(self):
        return self._rd.years

    @property
    def _timedelta(self):
        return self._td

    def total_seconds(self) -> float:
        if self.months == 0 and self.years == 0:
            return self._td.total_seconds()
        estimated_days = (self.years * 365) + (self.months * 30.5)
        warnings.warn(
            "Calculating total_seconds approximately. Months are considered as 30.5 days and years as 365 days.",
            UserWarning,
        )
        return self._td.total_seconds() + estimated_days * 86400

    def __add__(
        self, other: datetime | Itimedelta | timedelta
    ) -> datetime | "Flextimedelta":
        if isinstance(other, datetime):
            return other + self._td + self._rd
        if isinstance(other, Itimedelta):
            return Flextimedelta(
                _td=self._td + other._td,  # Soma as partes timedelta
                _rd=self._rd + other._rd,  # Soma as partes relativedelta
            )
        if isinstance(other, timedelta):
            return Flextimedelta(
                _td=self._td + other,  # Soma apenas a parte de timedelta
                _rd=self._rd,  # Mantém a parte de relativedelta inalterada
            )

        return NotImplemented

    def __radd__(
        self, other: datetime | Itimedelta | timedelta
    ) -> datetime | "Flextimedelta":
        return self + other

    def __sub__(self, other):
        if isinstance(other, Flextimedelta):
            new_td = self._td - other._td
            new_rd = self._rd - other._rd
            return Flextimedelta(_td=new_td, _rd=new_rd)
        elif isinstance(other, datetime):
            return other - self._td - self._rd
        elif isinstance(other, timedelta):
            new_td = self._td - other
            return Flextimedelta(_td=new_td, _rd=self._rd)
        elif isinstance(other, Itimedelta):
            new_td = self._td - other._td
            new_rd = self._rd - other._rd
            return Flextimedelta(_td=new_td, _rd=new_rd)

        return NotImplemented

    def __rsub__(self, other: datetime | Itimedelta | timedelta):
        return -(self - other)

    # def __sub__(self, other):
    #     if isinstance(other, datetime):
    #         return other - self._rd - self._td
    #     if isinstance(other, timedelta):
    #         return Flextimedelta.from_parts(self._td - other, self._rd)
    #     if isinstance(other, Flextimedelta):
    #         return Flextimedelta.from_parts(self._td - other._td, self._rd - other._rd)
    #     return NotImplemented

    # def __rsub__(self, other):
    #     if isinstance(other, datetime):
    #         return other - self._rd - self._td
    #     if isinstance(other, timedelta):
    #         return Flextimedelta.from_parts(other - self._td, -self._rd)
    #     return NotImplemented

    # def __neg__(self):
    #     return Flextimedelta.from_parts(-self._td, -self._rd)

    # def __pos__(self):
    #     return self

    # def __abs__(self):
    #     return Flextimedelta.from_parts(
    #         abs(self._td),
    #         relativedelta(years=abs(self._rd.years), months=abs(self._rd.months)),
    #     )

    # def __mul__(self, other):
    #     if not isinstance(other, (int, float)):
    #         return NotImplemented
    #     if isinstance(other, float) and not other.is_integer():
    #         raise ValueError(
    #             "Multiplication of years/months with non-integer is ambiguous."
    #         )
    #     return Flextimedelta.from_parts(
    #         self._td * other,
    #         relativedelta(
    #             years=int(self._rd.years * other), months=int(self._rd.months * other)
    #         ),
    #     )

    # __rmul__ = __mul__

    # def __floordiv__(self, other):
    #     if isinstance(other, (int, float)):
    #         return Flextimedelta(seconds=self.total_seconds() // other)
    #     elif isinstance(other, Flextimedelta):
    #         return int(self.total_seconds() // other.total_seconds())
    #     return NotImplemented

    # def __truediv__(self, other):
    #     if isinstance(other, (int, float)):
    #         return Flextimedelta(seconds=self.total_seconds() / other)
    #     elif isinstance(other, Flextimedelta):
    #         return self.total_seconds() / other.total_seconds()
    #     return NotImplemented

    # def __mod__(self, other):
    #     if isinstance(other, int):
    #         return Flextimedelta(seconds=self.total_seconds() % other)
    #     elif isinstance(other, Flextimedelta):
    #         return Flextimedelta(seconds=self.total_seconds() % other.total_seconds())
    #     return NotImplemented

    # def __divmod__(self, other):
    #     if isinstance(other, Flextimedelta):
    #         q = int(self.total_seconds() // other.total_seconds())
    #         r_secs = self.total_seconds() % other.total_seconds()
    #         return q, Flextimedelta(seconds=r_secs)
    #     return NotImplemented

    # def __eq__(self, other):
    #     return (
    #         isinstance(other, Flextimedelta)
    #         and self._td == other._td
    #         and self._rd == other._rd
    #     )

    # def __lt__(self, other):
    #     return self.total_seconds() < other.total_seconds()

    # def __le__(self, other):
    #     return self.total_seconds() <= other.total_seconds()

    # def __gt__(self, other):
    #     return self.total_seconds() > other.total_seconds()

    # def __ge__(self, other):
    #     return self.total_seconds() >= other.total_seconds()

    # def __hash__(self):
    #     return hash(
    #         (self.days, self.seconds, self.microseconds, self.months, self.years)
    #     )

    # def __bool__(self):
    #     return bool(self._td) or bool(self._rd)

    # def __reduce__(self):
    #     return (
    #         self.__class__,
    #         (self.days, self.seconds, self.microseconds, self.months, self.years),
    #     )

    # def __repr__(self):
    #     return (
    #         f"Flextimedelta(days={self.days}, seconds={self.seconds}, microseconds={self.microseconds}, "
    #         f"months={self.months}, years={self.years})"
    #     )

    # __str__ = __repr__

    # def to_relativedelta(self) -> relativedelta:
    #     return relativedelta(
    #         years=self._rd.years,
    #         months=self._rd.months,
    #         days=self._td.days,
    #         seconds=self._td.seconds,
    #         microseconds=self._td.microseconds,
    #     )

    # @classmethod
    # def from_parts(cls, td: timedelta, rd: relativedelta) -> "Flextimedelta":
    #     return cls(td.days, td.seconds, td.microseconds, rd.months, rd.years)
