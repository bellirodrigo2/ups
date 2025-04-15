from typing import Any, Generator

import pytest
from sqlalchemy.orm import Session, sessionmaker

from infra.db.db import get_db, make_session
from infra.db.models.base import Base

SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def session_local() -> sessionmaker[Session]:
    return make_session(SQLITE_URL, Base)


@pytest.fixture
def session(session_local: sessionmaker[Session]) -> Generator[Session, Any, None]:
    yield from get_db(session_local)
