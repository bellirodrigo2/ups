from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, json_column


class Recurrence(Base):
    __tablename__ = "recurrence"

    id: Mapped[str] = mapped_column(primary_key=True)
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
