from typing import Any

from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, CreatedAt, json_column

# from infra.db.models.fupgen import FupGen


class Data(Base, CreatedAt):
    __tablename__ = "fupgen_data"

    id: Mapped[str] = mapped_column(primary_key=True)
    data: Mapped[dict[str, Any]] = json_column(nullable=False)

    fupgen: Mapped["FupGen"] = relationship(back_populates="data", uselist=False)
