import uvicorn

from neis_mcp.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run("neis_mcp.server:app", host=settings.mcp_host, port=settings.mcp_port, reload=False)


if __name__ == "__main__":
    main()
