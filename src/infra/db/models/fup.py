from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, JSONList
from infra.db.models.fupgen import FollowupGeneratorModel


class FollowUpModel(Base):
    __tablename__ = "followups"

    fupid: Mapped[str] = mapped_column(primary_key=True)
    fupgenid: Mapped[str] = mapped_column(String, ForeignKey("fup_generators.id"))
    date: Mapped[datetime]

    responses: Mapped[list[tuple[str, dict[str, str]]]] = mapped_column(
        JSONList, default=[]
    )

    generator: Mapped["FollowupGeneratorModel"] = relationship(
        "FollowupGeneratorModel", backref="followups"
    )
