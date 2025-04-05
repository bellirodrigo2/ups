from dataclasses import dataclass
from typing import Any

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.usecase import UseCase
from domain.entity.fupgen import FollowupGenerator


@dataclass
class FupReadConfig:
    hookid: str | None = None
    ownerid: str | None = None
    name: str | None = None
    active: bool | None = None
    channel: str | None = None
    metahas: dict[str, Any] | None = None
    description: str | None = None


@dataclass
class ReadFupGenerator(UseCase):
    fup_gen_repo: FupGenRepository

    def execute(
        self, owner: str, fupg_config: FupReadConfig | None = None
    ) -> list[FollowupGenerator]:
        return self.fup_gen_repo.read_fupgen()
