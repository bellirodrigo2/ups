from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base, json_column


class Recurrence(Base):
    __tablename__ = "recurrence"

    id: Mapped[str] = mapped_column(primary_key=True)
    freq: Mapped[str]
    dtstart: Mapped[datetime]
    interval: Mapped[int] = mapped_column(default=1)
    count: Mapped[Optional[int]]
    until: Mapped[Optional[datetime]]
    byweekday: Mapped[Optional[List[str]]] = json_column(nullable=True)
    bymonthday: Mapped[Optional[List[int]]] = json_column(nullable=True)
    allow_infinite: Mapped[bool] = mapped_column(default=False)
    last_run: Mapped[Optional[datetime]]
    next_run: Mapped[Optional[datetime]]
    past_events: Mapped[str] = mapped_column(default="lastonly")
