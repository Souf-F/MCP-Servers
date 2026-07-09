#!/usr/bin/env python3
"""Programming Learning MCP Server.

This server exposes a small local dataset of programming topics through
MCP tools and resources, so a connected agent can help a student figure
out what to study next.

Tools:
- search_topics: search topics by title or key concept.
- get_topic_details: return the full record for one topic id.

Resource (added in a later task):
- topic catalog (read-only).
"""

import json
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("Programming Learning Server")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "topics.json"


def _load_topics() -> list[dict]:
    """Load the topic dataset from data/topics.json.

    Returns an empty list if the file is missing or invalid, so tools
    can fail gracefully instead of crashing the server.
    """
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return data.get("topics", [])


@mcp.tool
def search_topics(query: str) -> list[dict]:
    """Search programming topics by title or key concept.

    Args:
        query: free-text search term (case-insensitive), matched against
            each topic's title and key_concepts.

    Returns:
        A list of small topic summaries (id, title, summary) for every
        topic that matches. An empty list if nothing matches or the
        query is empty.
    """
    query = (query or "").strip().lower()
    if not query:
        return []

    results = []
    for topic in _load_topics():
        title = topic.get("title", "").lower()
        key_concepts = [kc.lower() for kc in topic.get("key_concepts", [])]

        if query in title or any(query in kc for kc in key_concepts):
            results.append({
                "id": topic.get("id"),
                "title": topic.get("title"),
                "summary": topic.get("summary"),
            })

    return results


@mcp.tool
def get_topic_details(topic_id: str) -> dict:
    """Return full information for a topic by id.

    Args:
        topic_id: exact id of the topic (e.g. "python-decorators").

    Returns:
        The full topic record (id, title, summary, prerequisites,
        key_concepts, common_mistakes, practice_idea) if found.
        Otherwise a dict with an "error" key explaining that the id
        was not found.
    """
    topic_id = (topic_id or "").strip()
    if not topic_id:
        return {"error": "topic_id must not be empty."}

    for topic in _load_topics():
        if topic.get("id") == topic_id:
            return topic

    return {"error": f"No topic found with id '{topic_id}'."}


if __name__ == "__main__":
    mcp.run()