from dataclasses import dataclass
from typing import Any

from app.gateway.sendgateway import SendGateway as SendGatewayInterface
from domain.entity.fup import FollowUp


@dataclass
class SendGateway(SendGatewayInterface):
    gateways: list[SendGatewayInterface]

    def send(self, fups: list[FollowUp]) -> None:

        for gateway in self.gateways:
            gateway.send(fups)


@dataclass
class SendGatewayFiltered(SendGatewayInterface):
    channel: str

    def _send(self, fups: list[FollowUp]) -> Any:
        # send deve atualizar fups responses
        raise NotImplementedError("Subclasses should implement _send")

    def send(self, fups: list[FollowUp]) -> None:

        filtered_fups = [
            fup
            for fup in fups
            if any(channel.type == self.channel for channel in fup.responses)
        ]

        self._send(filtered_fups)


if __name__ == "__main__":
    ...
