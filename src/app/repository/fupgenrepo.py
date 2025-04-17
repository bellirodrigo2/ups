from datetime import datetime
from typing import Protocol

from domain.entity.fupgen import FollowupGenerator, FupGenInput


class FupGenRepository(Protocol):
    def create(self, input: FupGenInput) -> datetime | None: ...

    def get_fupgen_id_by_owner_name(self, ownerid: str, name: str) -> str | None: ...

    def get_fupgen(
        self, ownerid: str, active_only: bool
    ) -> list[FollowupGenerator]: ...

    def update_config(
        self,
        updates: list[tuple[str, bool, int | None, datetime | None, datetime | None]],
    ) -> None: ...

    def update_exhaust_rule(
        self, fupgen_id: str, add_count: int | None, until: datetime | None
    ) -> None: ...

    def delete_fupgen(self, fupgen_id: str) -> None: ...
