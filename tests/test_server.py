from starlette.requests import Request

from neis_mcp.server import _accepts_sse, _is_allowed_origin, _validate_protocol_version
from neis_mcp.settings import Settings


def make_request(headers: dict[str, str]) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/mcp",
            "headers": [(key.lower().encode(), value.encode()) for key, value in headers.items()],
        }
    )


def test_allowed_origin_exact_host_with_any_port_when_port_is_omitted() -> None:
    settings = Settings(ALLOWED_ORIGINS="http://client.local")

    assert _is_allowed_origin("http://client.local:5173", settings)


def test_allowed_origin_regex_is_honored() -> None:
    settings = Settings(
        ALLOWED_ORIGINS="http://localhost",
        ALLOWED_ORIGIN_REGEX=r"https?://10\.0\.0\.\d+(:\d+)?",
    )

    assert _is_allowed_origin("http://10.0.0.12:3000", settings)


def test_accepts_sse_is_case_insensitive() -> None:
    request = make_request({"Accept": "Application/JSON, Text/Event-Stream"})

    assert _accepts_sse(request)


def test_validate_protocol_version_rejects_unsupported_header() -> None:
    request = make_request({"MCP-Protocol-Version": "2099-01-01"})

    response = _validate_protocol_version(request)

    assert response is not None
    assert response.status_code == 400


def test_validate_protocol_version_allows_missing_header() -> None:
    assert _validate_protocol_version(make_request({})) is None
