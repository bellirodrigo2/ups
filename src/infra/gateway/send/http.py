from dataclasses import dataclass
from typing import Any, Callable, Literal

from domain.entity.fup import FollowUp
from infra.gateway.sendgateway import SendGatewayFiltered
from infra.http.client import HTTPRequest


@dataclass
class HttpGatewayAdapter(SendGatewayFiltered):
    httpreq: HTTPRequest
    get_method: Callable[
        [dict[str, Any]], Literal["get", "post", "put", "patch", "head", "delete"]
    ]
    get_url: Callable[[dict[str, Any]], str]
    channel: str = "http"

    def _send(self, fups: list[FollowUp]) -> None:

        for fup in fups:

            for ch in fup.responses:
                if ch.type != self.channel:
                    continue

                method = self.get_method(ch.data)
                url = self.get_url(ch.data)

                if method == "get":
                    response = self.httpreq.get(url)
                else:
                    body: dict[str, str | dict[str, Any]] = {
                        "msg": fup.msg,
                        "data": ch.data,
                    }
                    response = self.httpreq.post(url, body)

                fup.update_response(ch.name, response)
