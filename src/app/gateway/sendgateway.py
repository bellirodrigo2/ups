from typing import Protocol

from domain.entity.fup import FollowUp


class SendGateway(Protocol):
    async def send(self, fups: list[FollowUp]) -> None: ...
