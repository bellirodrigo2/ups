from typing import List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, CreatedAt
from infra.db.models.channel import ChannelDB
from infra.db.models.data import Data
from infra.db.models.msg import Message
from infra.db.models.recurrenceconfig import Recurrence


class FupGen(Base, CreatedAt):
    __tablename__ = "fupgen"

    id: Mapped[str] = mapped_column(primary_key=True)
    hookid: Mapped[str]
    ownerid: Mapped[str]
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]]

    recurrence: Mapped["Recurrence"] = relationship(
        back_populates="fupgen",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    channels: Mapped[List["ChannelDB"]] = relationship(
        back_populates="fupgen", cascade="all, delete-orphan"
    )

    message_id: Mapped[str] = mapped_column(ForeignKey("fupgen_msg.id"), unique=True)
    message: Mapped["Message"] = relationship(back_populates="fupgen", uselist=False)

    data_id: Mapped[str] = mapped_column(ForeignKey("fupgen_data.id"), unique=True)
    data: Mapped["Data"] = relationship(back_populates="fupgen", uselist=False)

    __table_args__ = (UniqueConstraint("ownerid", "name", name="uq_owner_name"),)

    def __str__(self) -> str:
        return f"FupGen(id={self.id}, ownerid={self.ownerid}, name={self.name}, recurrence:{self.recurrence})"
