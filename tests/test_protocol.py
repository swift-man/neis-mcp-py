from typing import Any, Dict, Mapping

import pytest

from neis_mcp.protocol import McpProtocolHandler


class DummyToolService:
    def list_tools(self) -> list:
        return [{"name": "dummy", "inputSchema": {"type": "object", "properties": {}}}]

    async def call_tool(self, name: str, arguments: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "content": [{"type": "text", "text": name}],
            "structuredContent": {"arguments": dict(arguments)},
            "isError": False,
        }


@pytest.mark.asyncio
async def test_initialize_returns_tools_capability() -> None:
    handler = McpProtocolHandler(DummyToolService())  # type: ignore[arg-type]
    response = await handler.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"},
        }
    )

    assert response["result"]["protocolVersion"] == "2025-06-18"
    assert "tools" in response["result"]["capabilities"]


@pytest.mark.asyncio
async def test_initialize_rejects_non_object_params() -> None:
    handler = McpProtocolHandler(DummyToolService())  # type: ignore[arg-type]
    response = await handler.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": ["2025-06-18"],
        }
    )

    assert response["error"]["code"] == -32602
    assert response["error"]["message"] == "initialize params must be an object"


@pytest.mark.asyncio
async def test_tools_list_returns_registered_tools() -> None:
    handler = McpProtocolHandler(DummyToolService())  # type: ignore[arg-type]
    response = await handler.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})

    assert response["result"]["tools"][0]["name"] == "dummy"


@pytest.mark.asyncio
async def test_notification_returns_no_response() -> None:
    handler = McpProtocolHandler(DummyToolService())  # type: ignore[arg-type]
    response = await handler.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})

    assert response is None


@pytest.mark.asyncio
async def test_json_rpc_response_returns_no_response() -> None:
    handler = McpProtocolHandler(DummyToolService())  # type: ignore[arg-type]
    response = await handler.handle({"jsonrpc": "2.0", "id": 10, "result": {}})

    assert response is None
