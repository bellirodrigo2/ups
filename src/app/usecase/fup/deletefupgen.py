import logging
from dataclasses import dataclass, field
from logging import Logger

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.task.runtask import RunTask
from app.usecase.usecase import UseCase


@dataclass
class DeleteFupGenerator(UseCase):
    fupgenrepo: FupGenRepository
    runtask: RunTask

    logger: Logger = field(default_factory=logging.getLogger)

    async def execute(
        self, fupgen_id: str | None, owner: str | None = None, name: str | None = None
    ) -> None:

        if fupgen_id is None:
            if owner is None or name is None:
                raise Exception(
                    f"""To delelete a FupGenerator, an id, or (owner, name) should be provided: 
                                id:{fupgen_id},owner:{owner},name:{name}"""
                )
            fupgen_id = self.fupgenrepo.get_fupgen_id_by_owner_name(owner, name)
            if fupgen_id is None:
                raise Exception(f"There is no Fupgen for: owner={owner}, name={name}")

        self.fupgenrepo.delete_fupgen(fupgen_id)
