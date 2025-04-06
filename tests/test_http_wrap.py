import asyncio

import pytest
import responses
from aioresponses import aioresponses

from infra.http.client import AsyncRequest, SyncRequest  # atualize o caminho correto

# ---------- ASYNC TESTS ----------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method, data",
    [
        ("get", None),
        ("post", {"key": "value"}),
        ("put", {"key": "value"}),
        ("patch", {"key": "value"}),
        ("delete", None),
        ("head", None),
    ],
)
async def test_async_http_methods(method, data):
    url = "https://example.com/test"
    expected_status = 200
    expected_body = b"hello"
    expected_text = "hello"

    with aioresponses() as mock:
        mock_kwargs = {"status": expected_status, "body": expected_body}
        getattr(mock, method)(url, **mock_kwargs)

        async with AsyncRequest() as requester:
            func = getattr(requester, method)
            if data:
                resp = await func(url, data)
            else:
                resp = await func(url)

        assert resp.status_code == expected_status
        if method != "head":
            assert await resp.response == expected_text
            assert await resp.content == expected_body
        assert resp.url == url


# ---------- SYNC TESTS ----------


@pytest.mark.parametrize(
    "method, data",
    [
        ("get", None),
        ("post", {"key": "value"}),
        ("put", {"key": "value"}),
        ("patch", {"key": "value"}),
        ("delete", None),
        ("head", None),
    ],
)
def test_sync_http_methods(method, data):
    url = "https://example.com/test"
    expected_status = 200
    expected_body = b"hello"
    expected_text = "hello"

    with responses.RequestsMock() as mock:
        if method == "head":
            mock.add(
                getattr(responses, method.upper()),
                url,
                status=expected_status,
                content_type="text/plain",
            )
        else:
            mock.add(
                getattr(responses, method.upper()),
                url,
                body=expected_body,
                status=expected_status,
                content_type="text/plain",
            )

        requester = SyncRequest()
        func = getattr(requester, method)
        if data:
            resp = func(url, data)
        else:
            resp = func(url)

        assert resp.status_code == expected_status
        if method != "head":
            assert resp.response == expected_text
            assert resp.content == expected_body
        assert resp.url == url
