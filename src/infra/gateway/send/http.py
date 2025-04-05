
from dataclasses import dataclass
from typing import Any, Callable, Literal
from domain.entity.fup import FollowUp
from infra.gateway.sendgateway import SendGatewayFiltered
from infra.http.client import HTTPRequest


@dataclass
class HttpGatewayAdapter(SendGatewayFiltered):
    httpreq: HTTPRequest
    get_url: Callable[[dict[str, Any]], str]
    channel: str = 'http'

    def _send(self, fups: list[FollowUp]) -> None:
        
        for fup in fups:
            url = self.get_url(fup.data)
            body:dict[str, str | dict[str, Any]] = {
                'msg': fup.msg,
                'data': fup.data,
            }
            response = self.httpreq.post(url, body)
            fup.update_response(self.channel, response)          
