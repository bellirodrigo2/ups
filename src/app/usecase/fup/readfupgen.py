from dataclasses import dataclass
from typing import Any

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.usecase import UseCase
from domain.entity.fupgen import FollowupGenerator


class FupReadConfig:
    hookid: str | None = None
    owner: str | None = None
    name: str | None = None
    active: bool | None = None
    channel: str | None = None
    metahas: dict[str, Any] | None = None
    description: str | None = None


@dataclass
class RedFupGenerator(UseCase):
    fup_gen_repo: FupGenRepository

    def execute(
        self, owner: str, fupg_config: FupReadConfig
    ) -> list[FollowupGenerator]:
        return []
