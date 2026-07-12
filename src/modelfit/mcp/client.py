import os
from collections.abc import Mapping

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import Connection, StreamableHttpConnection


class MCPClientManager:
    def __init__(self, connections: Mapping[str, Connection]) -> None:
        self._connections: dict[str, Connection] = dict(connections)
        self._client = MultiServerMCPClient(self._connections)

    @staticmethod
    def _http_connection(url: str) -> StreamableHttpConnection:
        return {
            "transport": "streamable_http",
            "url": url,
        }

    @classmethod
    def from_environment(cls) -> "MCPClientManager":
        connections: dict[str, Connection] = {
            "document": cls._http_connection(
                os.getenv(
                    "MODELFIT_MCP_DOCUMENT_URL",
                    "http://localhost:9101/mcp",
                )
            ),
            "image": cls._http_connection(
                os.getenv(
                    "MODELFIT_MCP_IMAGE_URL",
                    "http://localhost:9102/mcp",
                )
            ),
        }

        web_url = os.getenv("MODELFIT_MCP_WEB_URL")
        if web_url:
            connections["web"] = cls._http_connection(web_url)

        return cls(connections)

    async def get_tools(self) -> list[BaseTool]:
        return await self._client.get_tools()
