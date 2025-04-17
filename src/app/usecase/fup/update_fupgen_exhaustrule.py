import logging
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.usecase import UseCase


@dataclass
class UpdateFupGenExhaustRule(UseCase):
    fupgenrepo: FupGenRepository

    logger: Logger = field(default_factory=logging.getLogger)

    async def execute(
        self, fupgen_id: str, add_count: int | None, until: datetime | None
    ) -> None:

        if add_count is None and until is None:
            raise Exception()

        self.fupgenrepo.update_exhaust_rule(fupgen_id, add_count, until)
