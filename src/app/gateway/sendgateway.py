from typing import Protocol

from domain.entity.fup import FollowUp


class SendGateway(Protocol):
    def send(self, fups: list[FollowUp]) -> None: ...
