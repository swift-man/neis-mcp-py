from typing import Any, Dict, Mapping, Optional

from neis_mcp import __version__
from neis_mcp.tool_service import ToolService

JSONRPC_VERSION = "2.0"
SUPPORTED_PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]


class McpProtocolHandler:
    """Small MCP JSON-RPC handler for Streamable HTTP transport."""

    def __init__(self, tool_service: ToolService) -> None:
        self._tool_service = tool_service

    async def handle(self, message: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(message, Mapping):
            return self._error_response(None, -32600, "Invalid Request")

        request_id = message.get("id")
        if message.get("jsonrpc") != JSONRPC_VERSION:
            return self._error_response(request_id, -32600, "Invalid JSON-RPC version")

        method = message.get("method")
        if not method:
            return self._handle_notification_or_response(message)

        if request_id is None:
            return self._handle_notification(method)

        if method == "initialize":
            params = self._request_params(message)
            if not isinstance(params, Mapping):
                return self._error_response(request_id, -32602, "initialize params must be an object")
            return self._response(request_id, self._initialize_result(params))
        if method == "ping":
            return self._response(request_id, {})
        if method == "tools/list":
            return self._response(request_id, {"tools": self._tool_service.list_tools()})
        if method == "tools/call":
            return await self._handle_tool_call(request_id, self._request_params(message))

        return self._error_response(request_id, -32601, f"Method not found: {method}")

    def _handle_notification_or_response(self, message: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        if "result" in message or "error" in message:
            return None
        if "id" in message:
            return self._error_response(message.get("id"), -32600, "Invalid Request")
        return None

    def _handle_notification(self, method: str) -> Optional[Dict[str, Any]]:
        if method in {"notifications/initialized", "notifications/cancelled"}:
            return None
        return None

    def _request_params(self, message: Mapping[str, Any]) -> Any:
        params = message.get("params", {})
        return {} if params is None else params

    async def _handle_tool_call(self, request_id: Any, params: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(params, Mapping):
            return self._error_response(request_id, -32602, "tools/call params must be an object")

        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(name, str) or not name:
            return self._error_response(request_id, -32602, "tools/call requires a tool name")
        if not isinstance(arguments, Mapping):
            return self._error_response(request_id, -32602, "tools/call arguments must be an object")

        result = await self._tool_service.call_tool(name, arguments)
        return self._response(request_id, result)

    def _initialize_result(self, params: Mapping[str, Any]) -> Dict[str, Any]:
        requested_version = str(params.get("protocolVersion") or SUPPORTED_PROTOCOL_VERSIONS[0])
        protocol_version = (
            requested_version
            if requested_version in SUPPORTED_PROTOCOL_VERSIONS
            else SUPPORTED_PROTOCOL_VERSIONS[0]
        )
        return {
            "protocolVersion": protocol_version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {
                "name": "neis-mcp-py",
                "title": "NEIS Open API MCP Server",
                "version": __version__,
            },
            "instructions": (
                "NEIS Open API 12종을 조회하는 읽기 전용 MCP 서버입니다. "
                "인증키는 KEY 인자 또는 NEIS_API_KEY 환경 변수로 전달할 수 있습니다."
            ),
        }

    def _response(self, request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}

    def _error_response(
        self,
        request_id: Any,
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        error: Dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": error}
