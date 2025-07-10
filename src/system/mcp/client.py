from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "web": {
            "transport": "sse",
            "url": "http://mcp:8082/sse",
        }
    }
)