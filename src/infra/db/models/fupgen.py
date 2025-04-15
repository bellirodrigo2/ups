from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, CreatedAt
from infra.db.models.channel import Channel
from infra.db.models.data import Data
from infra.db.models.msg import Message
from infra.db.models.recurrenceconfig import Recurrence


class FupGen(Base, CreatedAt):
    __tablename__ = "fupgen"

    id: Mapped[str] = mapped_column(primary_key=True)
    hookid: Mapped[str]
    ownerid: Mapped[str]
    name: Mapped[str]
    description: Mapped[Optional[str]]
    default_cycle: Mapped[int]

    recurrence_id: Mapped[str] = mapped_column(ForeignKey("recurrence.id"), unique=True)
    recurrence: Mapped["Recurrence"] = relationship()

    channels: Mapped[List["Channel"]] = relationship(
        back_populates="fupgen", cascade="all, delete-orphan"
    )

    message_id: Mapped[str] = mapped_column(ForeignKey("fupgen_msg.id"), unique=True)
    message: Mapped["Message"] = relationship(back_populates="fupgen", uselist=False)

    data_id: Mapped[str] = mapped_column(ForeignKey("fupgen_data.id"), unique=True)
    data: Mapped["Data"] = relationship(back_populates="fupgen", uselist=False)


# new_msg = Message(id=str(uuid4()), content="nova mensagem")
# session.add(new_msg)

# fupgen.message = new_msg
