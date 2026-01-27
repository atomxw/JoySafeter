from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    import os
    port = int(os.getenv("DEMO_MCP_SERVER_PORT", "8001"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
