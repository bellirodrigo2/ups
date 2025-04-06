from typing import Protocol

from domain.entity.fup import FollowUp


class FupRepository(Protocol):

    def add(self, fups: list[FollowUp]) -> None: ...
