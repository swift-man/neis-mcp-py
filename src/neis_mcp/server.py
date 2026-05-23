import json
import re
import secrets
from typing import Any, AsyncIterator, Dict, Optional
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from neis_mcp.api_catalog import API_DEFINITIONS
from neis_mcp.client import NeisApiClient
from neis_mcp.protocol import McpProtocolHandler
from neis_mcp.settings import Settings, get_settings
from neis_mcp.tool_service import ToolService

settings = get_settings()
client = NeisApiClient(settings)
tool_service = ToolService(client)
protocol_handler = McpProtocolHandler(tool_service)

app = FastAPI(
    title="NEIS MCP Server",
    description="NEIS Open API 12종을 제공하는 MCP Streamable HTTP 서버",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.allowed_origin_regex or None,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*", "Authorization"],
    expose_headers=["Mcp-Session-Id", "MCP-Protocol-Version"],
)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "name": "neis-mcp-py",
        "mcp_endpoint": "/mcp",
        "api_count": len(API_DEFINITIONS),
        "auth_required": bool(settings.mcp_auth_token),
    }


@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/mcp")
async def mcp_post(request: Request) -> Response:
    origin_error = _validate_origin(request)
    if origin_error is not None:
        return origin_error
    auth_error = _validate_auth(request)
    if auth_error is not None:
        return auth_error

    try:
        message = await request.json()
    except json.JSONDecodeError:
        response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"},
        }
        return JSONResponse(response, status_code=400)

    response = await protocol_handler.handle(message)
    if response is None:
        return Response(status_code=202)

    if settings.mcp_stream_responses and _accepts_sse(request):
        return StreamingResponse(
            _single_sse_event(response),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    return JSONResponse(response)


@app.get("/mcp")
async def mcp_get(request: Request) -> Response:
    origin_error = _validate_origin(request)
    if origin_error is not None:
        return origin_error
    auth_error = _validate_auth(request)
    if auth_error is not None:
        return auth_error
    if not _accepts_sse(request):
        return Response(status_code=405)
    return StreamingResponse(
        _empty_sse_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.delete("/mcp")
async def mcp_delete() -> Response:
    return Response(status_code=405)


def _accepts_sse(request: Request) -> bool:
    return "text/event-stream" in request.headers.get("accept", "")


async def _single_sse_event(payload: Dict[str, Any]) -> AsyncIterator[str]:
    yield "event: message\n"
    yield "data: " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n\n"


async def _empty_sse_stream() -> AsyncIterator[str]:
    yield ": connected\n\n"


def _validate_origin(request: Request) -> Optional[Response]:
    origin = request.headers.get("origin")
    if not origin or _is_allowed_origin(origin, settings):
        return None
    return JSONResponse({"detail": "Origin is not allowed"}, status_code=403)


def _validate_auth(request: Request) -> Optional[Response]:
    if not settings.mcp_auth_token:
        return None

    authorization = request.headers.get("authorization", "")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return JSONResponse({"detail": "Missing bearer token"}, status_code=401)

    token = authorization[len(prefix) :]
    if not secrets.compare_digest(token, settings.mcp_auth_token):
        return JSONResponse({"detail": "Invalid bearer token"}, status_code=403)

    return None


def _is_allowed_origin(origin: str, settings_: Settings) -> bool:
    if "*" in settings_.allowed_origins:
        return True
    if settings_.allowed_origin_regex and re.fullmatch(settings_.allowed_origin_regex, origin):
        return True

    parsed_origin = urlsplit(origin)
    for allowed_origin in settings_.allowed_origins:
        parsed_allowed = urlsplit(allowed_origin)
        same_scheme = parsed_origin.scheme == parsed_allowed.scheme
        same_host = parsed_origin.hostname == parsed_allowed.hostname
        same_port = parsed_allowed.port is None or parsed_origin.port == parsed_allowed.port
        if same_scheme and same_host and same_port:
            return True
    return False
