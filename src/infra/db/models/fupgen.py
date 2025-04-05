from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from infra.db.models.base import Base, JSONEncoded


class FollowupGeneratorModel(Base):
    __tablename__ = "fup_generators"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    owner_id: Mapped[str] = mapped_column(String)

    name: Mapped[str] = mapped_column(String)
    msg: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    active: Mapped[bool] = mapped_column(Boolean)
    channel: Mapped[list[str]] = mapped_column(JSONEncoded)
    data: Mapped[dict[str, Any]] = mapped_column(JSONEncoded)

    created_at: Mapped[datetime] = mapped_column(DateTime)
    last_run: Mapped[datetime] = mapped_column(DateTime)

    recurrence_config: Mapped["RecurrenceConfigModel"] = relationship(
        "RecurrenceConfigModel",
        uselist=False,
        primaryjoin=(
            "and_("
            "FollowupGeneratorModel.id == foreign(RecurrenceConfigModel.owner_id), "
            "RecurrenceConfigModel.owner_type == 'fupgen'"
            ")"
        ),
        viewonly=True,
    )
