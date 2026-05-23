import httpx
import pytest

from neis_mcp.client import NeisApiClient
from neis_mcp.settings import Settings
from neis_mcp.tool_service import ToolService


@pytest.mark.asyncio
async def test_call_tool_returns_tool_error_for_unexpected_neis_json() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["unexpected"])

    client = NeisApiClient(Settings(), transport=httpx.MockTransport(handler))
    service = ToolService(client)

    result = await service.call_tool("get_school_info", {})

    assert result["isError"] is True
    assert result["structuredContent"]["error"] == "NEIS API returned an unexpected JSON response"
    await client.close()
