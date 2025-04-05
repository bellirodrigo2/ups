from datetime import datetime
from typing import Protocol

from domain.entity.fupgen import FupGenInput

# EXCECAP OWNER NAO EVISTE
# OWNER JA TEM GEN COM MESMO NOME


class FupGenRepository(Protocol):
    def create(self, id: str, fupgen: FupGenInput) -> datetime:
        # se owner existe,
        # se owner-name existe,
        ...
