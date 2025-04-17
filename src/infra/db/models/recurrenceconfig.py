from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, json_column


class Recurrence(Base):
    __tablename__ = "recurrence"

    id: Mapped[str] = mapped_column(ForeignKey("fupgen.id"), primary_key=True)
    freq: Mapped[str]
    dtstart: Mapped[datetime] = mapped_column(nullable=True)
    interval: Mapped[int] = mapped_column(default=1)
    count: Mapped[Optional[int]] = mapped_column(nullable=True)
    until: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    byweekday: Mapped[Optional[List[str]]] = json_column(nullable=True)
    bymonthday: Mapped[Optional[List[int]]] = json_column(nullable=True)
    allow_infinite: Mapped[bool] = mapped_column(default=True)
    last_run: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_exhausted: Mapped[bool] = mapped_column(default=False)
    past_events: Mapped[str] = mapped_column(default="lastonly")

    fupgen: Mapped["FupGen"] = relationship(back_populates="recurrence", uselist=False)

    def __str__(self) -> str:
        return (
            f"Recurrence(id={self.id}, freq={self.freq}, dtstart={self.dtstart}, "
            f"interval={self.interval}, count={self.count}, until={self.until}, "
            f"byweekday={self.byweekday}, bymonthday={self.bymonthday}, "
            f"allow_infinite={self.allow_infinite}, last_run={self.last_run}, "
            f"next_run={self.next_run}, is_exhausted={self.is_exhausted}, "
            f"past_events={self.past_events})"
        )
