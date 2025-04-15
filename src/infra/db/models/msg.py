from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.models.base import Base, CreatedAt

# from infra.db.models.fupgen import FupGen


class Message(Base, CreatedAt):
    __tablename__ = "fupgen_msg"

    id: Mapped[str] = mapped_column(primary_key=True)
    msg: Mapped[str] = mapped_column(nullable=False)
    fupgen: Mapped["FupGen"] = relationship(back_populates="message", uselist=False)
