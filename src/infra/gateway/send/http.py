
from dataclasses import dataclass
from typing import Any, Callable, Literal
from domain.entity.fup import FollowUp
from infra.gateway.sendgateway import SendGatewayFiltered
from infra.http.client import HTTPRequest


@dataclass
class HttpGatewayAdapter(SendGatewayFiltered):
    httpreq: HTTPRequest
    get_url: Callable[[dict[str, Any]], str]
    get_or_post: Callable[[dict[str, Any]], Literal['get', 'post']]
    channel: str = 'http'

    def _send(self, fups: list[FollowUp]) -> None:
        
        for fup in fups:
            url = self.get_url(fup.data)
            method = self.get_or_post(fup.data)

            response = self.httpreq.get(url) if method == 'get' else self.httpreq.post(url, fup.data)
            fup.update_response(self.channel, response)          
