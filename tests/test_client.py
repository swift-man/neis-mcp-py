import httpx
import pytest

from neis_mcp.api_catalog import API_DEFINITIONS
from neis_mcp.client import NeisApiClient, NeisApiError
from neis_mcp.settings import Settings


@pytest.mark.asyncio
async def test_fetch_normalizes_neis_response_and_redacts_key() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/hub/schoolInfo"
        assert request.url.params["Type"] == "json"
        assert request.url.params["pSize"] == "1"
        assert request.url.params["KEY"] == "secret"
        return httpx.Response(
            200,
            json={
                "schoolInfo": [
                    {
                        "head": [
                            {"list_total_count": 1},
                            {"RESULT": {"CODE": "INFO-000", "MESSAGE": "정상 처리되었습니다."}},
                        ]
                    },
                    {"row": [{"SCHUL_NM": "테스트고등학교"}]},
                ]
            },
        )

    client = NeisApiClient(
        Settings(NEIS_API_KEY="secret"),
        transport=httpx.MockTransport(handler),
    )

    result = await client.fetch(
        API_DEFINITIONS["get_school_info"],
        {"ATPT_OFCDC_SC_CODE": "T10", "pSize": 1},
    )
    await client.close()

    assert result.result["CODE"] == "INFO-000"
    assert result.total_count == 1
    assert result.rows == [{"SCHUL_NM": "테스트고등학교"}]
    assert result.request_params["KEY"] == "***"
    assert "KEY=%2A%2A%2A" in result.request_url


@pytest.mark.asyncio
async def test_fetch_rejects_unexpected_json_payload() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["unexpected"])

    client = NeisApiClient(Settings(), transport=httpx.MockTransport(handler))

    with pytest.raises(NeisApiError, match="unexpected JSON response"):
        await client.fetch(API_DEFINITIONS["get_school_info"], {})

    await client.close()


@pytest.mark.asyncio
async def test_fetch_reuses_http_client() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"RESULT": {"CODE": "INFO-000", "MESSAGE": "ok"}})

    client = NeisApiClient(Settings(), transport=httpx.MockTransport(handler))

    await client.fetch(API_DEFINITIONS["get_school_info"], {})
    first_client = client._client
    await client.fetch(API_DEFINITIONS["get_school_info"], {})

    assert client._client is first_client
    await client.close()


def test_build_params_rejects_too_large_page_size() -> None:
    client = NeisApiClient(Settings())
    with pytest.raises(NeisApiError):
        client.build_params(API_DEFINITIONS["get_school_info"], {"pSize": 1001})


def test_build_params_rejects_extra_params_overriding_validated_params() -> None:
    client = NeisApiClient(Settings())

    with pytest.raises(NeisApiError, match="cannot override"):
        client.build_params(API_DEFINITIONS["get_school_info"], {"extra_params": {"pSize": 1001}})


def test_build_params_rejects_extra_params_overriding_catalog_params() -> None:
    client = NeisApiClient(Settings())

    with pytest.raises(NeisApiError, match="cannot override"):
        client.build_params(
            API_DEFINITIONS["get_school_info"],
            {"extra_params": {"ATPT_OFCDC_SC_CODE": "T10"}},
        )
