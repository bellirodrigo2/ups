from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, CreatedAt, json_column

# from infra.db.models.fupgen import FupGen


class Channel(Base, CreatedAt):
    __tablename__ = "channel"

    id: Mapped[str] = mapped_column(primary_key=True)
    fupgen_id: Mapped[str] = mapped_column(ForeignKey("fupgen.id"))
    type: Mapped[str]
    configdata: Mapped[dict[str, Any]] = json_column(nullable=True)

    fupgen: Mapped["FupGen"] = relationship(back_populates="channels")
