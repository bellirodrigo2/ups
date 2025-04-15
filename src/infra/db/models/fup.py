from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base, CreatedAt


class fup(Base, CreatedAt):
    __tablename__ = "fup"

    id: Mapped[str] = mapped_column(primary_key=True)
    fupgenid: Mapped[str] = mapped_column(ForeignKey("fupgen.id"))
    msgid: Mapped[str] = mapped_column(ForeignKey("fupgen_msg.id"))
    dataid: Mapped[str] = mapped_column(ForeignKey("fupgen_data.id"))
    date: Mapped[datetime]

    # se quiser referenciar fupgen
    # fupgen: Mapped["FupGen"] = relationship()
    # message: Mapped["Message"] = relationship()
    # data: Mapped["Data"] = relationship()
