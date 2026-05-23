from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mcp_host: str = Field(default="127.0.0.1", alias="MCP_HOST")
    mcp_port: int = Field(default=8000, alias="MCP_PORT")
    mcp_auth_token: str = Field(default="", alias="MCP_AUTH_TOKEN")
    neis_api_key: str = Field(default="", alias="NEIS_API_KEY")
    neis_base_url: str = Field(default="https://open.neis.go.kr/hub", alias="NEIS_BASE_URL")
    request_timeout_seconds: float = Field(default=20.0, alias="REQUEST_TIMEOUT_SECONDS")
    mcp_stream_responses: bool = Field(default=True, alias="MCP_STREAM_RESPONSES")
    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost",
            "http://127.0.0.1",
            "http://[::1]",
            "https://localhost",
            "https://127.0.0.1",
        ],
        alias="ALLOWED_ORIGINS",
    )
    allowed_origin_regex: str = Field(
        default=r"https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?",
        alias="ALLOWED_ORIGIN_REGEX",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_allowed_origins(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() and not value.strip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


def get_settings() -> Settings:
    return Settings()
