from neis_mcp.server import _is_allowed_origin
from neis_mcp.settings import Settings


def test_allowed_origin_exact_host_with_any_port_when_port_is_omitted() -> None:
    settings = Settings(ALLOWED_ORIGINS="http://client.local")

    assert _is_allowed_origin("http://client.local:5173", settings)


def test_allowed_origin_regex_is_honored() -> None:
    settings = Settings(
        ALLOWED_ORIGINS="http://localhost",
        ALLOWED_ORIGIN_REGEX=r"https?://10\.0\.0\.\d+(:\d+)?",
    )

    assert _is_allowed_origin("http://10.0.0.12:3000", settings)
