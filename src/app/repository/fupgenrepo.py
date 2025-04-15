from datetime import datetime
from typing import Protocol

from domain.entity.fupgen import FollowupGenerator, FupGenInput


class FupGenRepository(Protocol):
    def create(self, id: str, fupgen: FupGenInput) -> datetime: ...

    def get_recur_config(
        self, ownerid: str, active: bool
    ) -> list[FollowupGenerator]: ...

    def update_config(
        self,
        updates: list[tuple[str, bool, int | None, datetime | None, datetime | None]],
    ) -> None: ...
