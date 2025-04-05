from datetime import datetime
from typing import Literal

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base, JSONList


class RecurrenceConfigModel(Base):
    __tablename__ = "recurrence_configs"

    id: Mapped[str] = mapped_column(primary_key=True)

    owner_type: Mapped[Literal["owner", "fupgen"]] = mapped_column(String)
    owner_id: Mapped[str] = mapped_column(String)

    freq: Mapped[str]
    dtstart: Mapped[datetime]
    interval: Mapped[int] = mapped_column(default=1)
    count: Mapped[int | None] = mapped_column(nullable=True)
    until: Mapped[datetime | None] = mapped_column(nullable=True)
    byweekday: Mapped[list[str] | None] = mapped_column(JSONList, nullable=True)
    bymonthday: Mapped[list[int] | None] = mapped_column(JSONList, nullable=True)
    allow_infinite: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        UniqueConstraint("owner_type", "owner_id", name="uq_recurrence_owner"),
    )
