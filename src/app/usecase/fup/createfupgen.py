from dataclasses import dataclass
from typing import Callable

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.usecase import UseCase
from domain.entity.fupgen import FupGenInput, FupGenOutput


@dataclass
class CreateFupGenerator(UseCase):
    fup_gen_repo: FupGenRepository
    makeid: Callable[[], str]

    def execute(self, fupgen: FupGenInput) -> FupGenOutput:

        id = self.makeid()

        created_at = self.fup_gen_repo.create(id, fupgen)

        return FupGenOutput(id=id, created_at=created_at)
