from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol, runtime_checkable

import aiohttp
import requests


@runtime_checkable
class ResponseInterface(Protocol):
    @property
    def status_code(self) -> int: ...
    @property
    def response(self) -> str: ...
    @property
    def content(self) -> bytes: ...
    @property
    def url(self) -> str: ...


@dataclass
class AiohttpResponse(ResponseInterface):
    status: int
    text: str
    content: bytes
    url: str

    @property
    def status_code(self) -> int:
        return self.status

    @property
    async def response(self) -> str:
        return self.text

    @property
    async def content(self) -> bytes:
        return self.content

    @property
    def url(self) -> str:
        return self.url


@dataclass
class RequestsResponse(ResponseInterface):
    _response: requests.Response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def response(self) -> str:
        return self._response.text

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def url(self) -> str:
        return str(self._response.url)


class HTTPRequest(Protocol):
    def get(self, url: str) -> ResponseInterface: ...
    def get_many(self, urls: list[str], n: int) -> Iterable[ResponseInterface]: ...
    def post(self, url: str, data: dict[str, Any]) -> ResponseInterface: ...
    def put(self, url: str, data: dict[str, Any]) -> ResponseInterface: ...
    def patch(self, url: str, data: dict[str, Any]) -> ResponseInterface: ...
    def delete(self, url: str) -> ResponseInterface: ...
    def head(self, url: str) -> ResponseInterface: ...


def sublist(lista: list[Any], n: int):
    return [lista[i : i + n] for i in range(0, len(lista), n)]


@dataclass
class AsyncRequest(HTTPRequest):
    session: aiohttp.ClientSession = field(default_factory=aiohttp.ClientSession)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def _request(
        self, method: str, url: str, data: dict[str, Any] | None = None
    ) -> ResponseInterface:
        request_fn = getattr(self.session, method)
        async with request_fn(url, json=data if data else None) as response:
            text = await response.text()
            content = await response.read()
            return AiohttpResponse(
                status=response.status,
                text=text,
                content=content,
                url=str(response.url),
            )

    async def get(self, url: str) -> ResponseInterface:
        return await self._request("get", url)

    async def get_many(self, urls: list[str], n: int):
        lists = sublist(urls, n)
        for li in lists:
            try:
                tasks = [self._request("get", url) for url in li]
                yield await asyncio.gather(*tasks)
            except Exception:
                yield li

    async def post(self, url: str, data: dict[str, Any]) -> ResponseInterface:
        return await self._request("post", url, data)

    async def put(self, url: str, data: dict[str, Any]) -> ResponseInterface:
        return await self._request("put", url, data)

    async def patch(self, url: str, data: dict[str, Any]) -> ResponseInterface:
        return await self._request("patch", url, data)

    async def delete(self, url: str) -> ResponseInterface:
        return await self._request("delete", url)

    async def head(self, url: str) -> ResponseInterface:
        return await self._request("head", url)


@dataclass
class SyncRequest(HTTPRequest):
    session: requests.Session = field(default_factory=requests.Session)

    def _request(
        self, method: str, url: str, data: dict[str, Any] | None = None
    ) -> ResponseInterface:
        request_fn = getattr(self.session, method)
        response = request_fn(url, json=data if data else None)
        return RequestsResponse(response)

    def get(self, url: str) -> ResponseInterface:
        return self._request("get", url)

    def get_many(self, urls: list[str], n: int):
        lists = sublist(urls, n)
        for li in lists:
            try:
                yield [self._request("get", url) for url in li]
            except Exception:
                yield li

    def post(self, url: str, data: dict[str, Any]) -> ResponseInterface:
        return self._request("post", url, data)

    def put(self, url: str, data: dict[str, Any]) -> ResponseInterface:
        return self._request("put", url, data)

    def patch(self, url: str, data: dict[str, Any]) -> ResponseInterface:
        return self._request("patch", url, data)

    def delete(self, url: str) -> ResponseInterface:
        return self._request("delete", url)

    def head(self, url: str) -> ResponseInterface:
        return self._request("head", url)
