from datetime import datetime
from typing import Protocol

from domain.entity.fupgen import FollowupGenerator, FupGenInput, FupGenReadConfig

# EXCECAP OWNER NAO EVISTE
# OWNER JA TEM GEN COM MESMO NOME


class FupGenRepository(Protocol):
    def create(self, id: str, fupgen: FupGenInput) -> datetime: ...

    def search(
        self, owner: str, config: FupGenReadConfig
    ) -> list[FollowupGenerator]: ...

    def update_lastrun(self, ids: list[str], last_run: datetime) -> None: ...
