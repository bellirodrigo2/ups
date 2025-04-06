from dataclasses import dataclass

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.usecase import UseCase
from domain.entity.fupgen import FollowupGenerator, FupGenReadConfig

@dataclass
class ReadFupGenerator(UseCase):
    fup_gen_repo: FupGenRepository

    def execute(
        self, owner: str, fupg_config: FupGenReadConfig | None = None
    ) -> list[FollowupGenerator]:
        
        fupg_config = fupg_config or FupGenReadConfig()
        return self.fup_gen_repo.search(owner, fupg_config)
