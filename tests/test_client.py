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

    assert result.result["CODE"] == "INFO-000"
    assert result.total_count == 1
    assert result.rows == [{"SCHUL_NM": "테스트고등학교"}]
    assert result.request_params["KEY"] == "***"
    assert "KEY=%2A%2A%2A" in result.request_url


def test_build_params_rejects_too_large_page_size() -> None:
    client = NeisApiClient(Settings())
    with pytest.raises(NeisApiError):
        client.build_params(API_DEFINITIONS["get_school_info"], {"pSize": 1001})
