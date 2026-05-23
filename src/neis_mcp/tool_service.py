import json
from typing import Any, Dict, List, Mapping

from neis_mcp.api_catalog import API_DEFINITIONS, list_api_definitions
from neis_mcp.client import NeisApiClient, NeisApiError
from neis_mcp.models import ApiParameter, NeisApiDefinition


class ToolService:
    """Builds MCP tool metadata and executes NEIS API tools."""

    def __init__(self, client: NeisApiClient) -> None:
        self._client = client

    def list_tools(self) -> List[Dict[str, Any]]:
        tools = [self._tool_schema(api) for api in list_api_definitions()]
        tools.append(self._metadata_tool_schema())
        return tools

    async def call_tool(self, name: str, arguments: Mapping[str, Any]) -> Dict[str, Any]:
        if name == "list_neis_open_apis":
            metadata = self._catalog_metadata()
            return self._success_result(metadata)

        api = API_DEFINITIONS.get(name)
        if api is None:
            return self._error_result(f"Unknown tool: {name}")

        unexpected = self._unexpected_arguments(api, arguments)
        if unexpected:
            return self._error_result("Unexpected argument(s): " + ", ".join(sorted(unexpected)))

        try:
            result = await self._client.fetch(api, arguments)
        except NeisApiError as exc:
            return self._error_result(str(exc))

        payload = result.model_dump()
        is_error = str(result.result.get("CODE", "")).upper().startswith("ERROR")
        return self._tool_result(payload, is_error=is_error)

    def _tool_schema(self, api: NeisApiDefinition) -> Dict[str, Any]:
        properties: Dict[str, Any] = {
            "KEY": {
                "type": "string",
                "description": "NEIS 인증키입니다. 생략하면 NEIS_API_KEY 환경 변수를 사용합니다.",
            },
            "pIndex": {
                "type": "integer",
                "minimum": 1,
                "default": 1,
                "description": "페이지 위치입니다.",
            },
            "pSize": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1000,
                "default": 100,
                "description": "페이지당 조회 건수입니다. NEIS 제한상 최대 1000입니다.",
            },
            "extra_params": {
                "type": "object",
                "additionalProperties": {"type": ["string", "number", "boolean"]},
                "description": "카탈로그에 없는 NEIS 추가 요청 파라미터가 필요할 때 사용합니다.",
            },
        }

        for parameter in api.parameters:
            properties[parameter.id] = self._parameter_schema(parameter)

        return {
            "name": api.tool_name,
            "title": api.title,
            "description": api.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": [parameter.id for parameter in api.parameters if parameter.required],
                "additionalProperties": False,
            },
            "annotations": {"readOnlyHint": True, "openWorldHint": True},
        }

    def _metadata_tool_schema(self) -> Dict[str, Any]:
        return {
            "name": "list_neis_open_apis",
            "title": "NEIS Open API 목록",
            "description": "이 MCP 서버가 제공하는 12개 NEIS Open API 메타데이터를 조회합니다.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            "annotations": {"readOnlyHint": True, "openWorldHint": False},
        }

    def _parameter_schema(self, parameter: ApiParameter) -> Dict[str, Any]:
        description = parameter.name_ko
        if parameter.description:
            description += f" - {parameter.description}"
        return {"type": parameter.value_type, "description": description}

    def _unexpected_arguments(self, api: NeisApiDefinition, arguments: Mapping[str, Any]) -> List[str]:
        allowed = {"KEY", "pIndex", "pSize", "extra_params"}
        allowed.update(parameter.id for parameter in api.parameters)
        return [key for key in arguments.keys() if key not in allowed]

    def _catalog_metadata(self) -> Dict[str, Any]:
        return {
            "count": len(API_DEFINITIONS),
            "apis": [
                {
                    "tool_name": api.tool_name,
                    "title": api.title,
                    "api_res": api.api_res,
                    "description": api.description,
                    "sample_url": api.sample_url,
                    "parameters": [parameter.model_dump() for parameter in api.parameters],
                }
                for api in list_api_definitions()
            ],
        }

    def _success_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._tool_result(payload, is_error=False)

    def _error_result(self, message: str) -> Dict[str, Any]:
        return self._tool_result({"error": message}, is_error=True)

    def _tool_result(self, payload: Dict[str, Any], is_error: bool) -> Dict[str, Any]:
        return {
            "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
            "structuredContent": payload,
            "isError": is_error,
        }
