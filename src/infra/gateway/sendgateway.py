from dataclasses import dataclass

from app.gateway.sendgateway import SendGateway as SendGatewayInterface
from domain.entity.fup import FollowUp


@dataclass
class SendGateway(SendGatewayInterface):
    gateways: list[SendGatewayInterface]

    def send(self, fups: list[FollowUp]) -> None:

        for gateway in self.gateways:
            gateway.send(fups)


@dataclass
class SendGatewayAdapter(SendGatewayInterface):
    channel: str

    def send(self, fups: list[FollowUp]) -> None:

        filtered_fups = [fup for fup in fups if self.channel in fup.response.get('channel', ())]
        if filtered_fups:
            super().send(filtered_fups)
            aqui tem que mudar...e send tem que retornar response e atualizar
