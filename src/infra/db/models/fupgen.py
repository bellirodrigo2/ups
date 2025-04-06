from datetime import datetime
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, JSONEncoded
from infra.db.models.recurrenceconfig import RecurrenceConfigModel


class FollowupGeneratorModel(Base):
    __tablename__ = "fup_generators"

    id: Mapped[str] = mapped_column(primary_key=True)
    owner_id: Mapped[str]
    name: Mapped[str]
    msg: Mapped[str]
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    active: Mapped[bool]
    channel: Mapped[list[str]] = mapped_column(JSONEncoded)
    data: Mapped[dict[str, Any]] = mapped_column(JSONEncoded)

    created_at: Mapped[datetime]
    last_run: Mapped[datetime]

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
