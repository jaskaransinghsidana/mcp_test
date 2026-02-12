import os
from datetime import datetime

from fastmcp import FastMCP

mcp = FastMCP("sample-mcp-tools")


@mcp.tool()
def weather_lookup(city: str) -> dict:
    """Return mocked weather details for a city."""
    city_norm = city.strip().lower()
    samples = {
        "san francisco": {"temp_c": 17, "condition": "foggy"},
        "new york": {"temp_c": 23, "condition": "sunny"},
        "london": {"temp_c": 14, "condition": "cloudy"},
    }
    details = samples.get(city_norm, {"temp_c": 20, "condition": "clear"})
    return {"city": city.title(), **details, "timestamp": datetime.utcnow().isoformat()}


@mcp.tool()
def kb_search(query: str) -> dict:
    """Simple local knowledge-base search simulation."""
    snippets = [
        "LangGraph uses directed stateful graphs to orchestrate agent behavior.",
        "MCP standardizes how AI apps discover and call external tools.",
        "FastMCP can implement MCP clients and servers with minimal boilerplate.",
    ]
    matches = [item for item in snippets if any(word.lower() in item.lower() for word in query.split())]
    return {"query": query, "matches": matches or snippets[:1]}


@mcp.tool()
def summarize_text(text: str) -> dict:
    """Return a tiny summary for arbitrary text."""
    words = text.split()
    summary = " ".join(words[:30]) + ("..." if len(words) > 30 else "")
    return {"summary": summary, "word_count": len(words)}


if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "9001"))
    mcp.run(transport="http", host=host, port=port, path="/mcp")
