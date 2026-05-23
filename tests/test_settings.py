from neis_mcp.settings import Settings


def test_allowed_origins_accepts_comma_separated_env_value() -> None:
    settings = Settings(ALLOWED_ORIGINS="http://client.local:3000,http://10.0.0.10:8080")

    assert settings.allowed_origins == ["http://client.local:3000", "http://10.0.0.10:8080"]


def test_server_host_and_port_are_configurable() -> None:
    settings = Settings(MCP_HOST="0.0.0.0", MCP_PORT=9000)

    assert settings.mcp_host == "0.0.0.0"
    assert settings.mcp_port == 9000
