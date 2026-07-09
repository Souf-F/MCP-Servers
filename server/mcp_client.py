#!/usr/bin/env python3
"""Small FastMCP client used to test learning_server.py directly.

This script connects to the server in-process (no need to run it as a
separate process first) and exercises every tool and resource, so we
can prove the server works before wiring it to an agent (Task 7).

Run from the project root:
    python3 client/mcp_client.py
"""

import asyncio
import sys
from pathlib import Path

# Make "server" importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))

from fastmcp import Client
from learning_server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        # 1. The server starts + tools are listed.
        tools = await client.list_tools()
        print("Tools disponibles:", [t.name for t in tools])

        resources = await client.list_resources()
        print("Resources disponibles:", [str(r.uri) for r in resources])

        # 2. search_topics with a valid query.
        print("\n--- search_topics('decorator') ---")
        result = await client.call_tool("search_topics", {"query": "decorator"})
        print(result.data)

        # 3. search_topics with a query that matches nothing.
        print("\n--- search_topics('nonexistent_topic_xyz') ---")
        result = await client.call_tool(
            "search_topics", {"query": "nonexistent_topic_xyz"}
        )
        print(result.data)

        # 4. get_topic_details with a valid id.
        print("\n--- get_topic_details('python-decorators') ---")
        result = await client.call_tool(
            "get_topic_details", {"topic_id": "python-decorators"}
        )
        print(result.data)

        # 5. get_topic_details with an invalid id (error case).
        print("\n--- get_topic_details('does-not-exist') ---")
        result = await client.call_tool(
            "get_topic_details", {"topic_id": "does-not-exist"}
        )
        print(result.data)

        # 6. Read the read-only catalog resource.
        print("\n--- read topics://catalog ---")
        result = await client.read_resource("topics://catalog")
        print(result[0].text)


if __name__ == "__main__":
    asyncio.run(main())
