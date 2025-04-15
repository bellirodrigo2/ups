from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm.session import Session


def make_session(
    url: str, base: type[DeclarativeBase], echo=False
) -> sessionmaker[Session]:
    engine = create_engine(url, echo=echo)

    base.metadata.create_all(engine)

    return sessionmaker(bind=engine)


def get_db(sessionLocal: sessionmaker[Session]):

    db = sessionLocal()
    try:
        yield db
    except Exception:
        # logger.exception("Session rollback because of exception")
        db.rollback()
        raise
    finally:
        db.close()
