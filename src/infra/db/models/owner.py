from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base
from infra.db.models.recurrenceconfig import RecurrenceConfigModel


class OwnerModel(Base):
    __tablename__ = "owners"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str]

    recurrence_config: Mapped["RecurrenceConfigModel"] = relationship(
        "RecurrenceConfigModel",
        uselist=False,
        primaryjoin=(
            "and_(OwnerModel.id == foreign(RecurrenceConfigModel.owner_id), "
            "RecurrenceConfigModel.owner_type == 'owner')"
        ),
        viewonly=True,
    )
