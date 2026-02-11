from __future__ import annotations

from typing import Any, Dict, Optional

from fastmcp.client import Client


class MCPToolClient:
    def __init__(self, server_url: str) -> None:
        self.server_url = server_url

    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        payload = arguments or {}
        async with Client(self.server_url) as client:
            return await client.call_tool(tool_name, payload)
