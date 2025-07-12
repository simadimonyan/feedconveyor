import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(".env")

client = MultiServerMCPClient(
    {
        "web": {
            "transport": "sse",
            "url": f"{os.getenv("MCP_SERVER_URL")}",
        }
    }
)