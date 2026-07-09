#!/usr/bin/env python3
"""Simple agent-like client that uses the MCP client to answer student
questions.

This is a deterministic agent (no LLM): it receives a student question,
connects to the MCP server as a real external process over stdio, calls
search_topics and get_topic_details THROUGH that MCP connection, and
formats a short student-facing answer from the returned data.

It never imports learning_server functions directly — everything goes
through fastmcp.Client talking MCP over stdio to a subprocess running
server/learning_server.py.

Run from the project root:
    python3 client/agent.py "I want to study Python decorators. What should I review first?"

If no argument is given, a default sample question is used.
"""

import asyncio
import re
import sys
from pathlib import Path

from fastmcp import Client

SERVER_SCRIPT = str(Path(__file__).resolve().parent.parent / "server" / "learning_server.py")

# Small stopword list used only to pick out meaningful words from the
# student's question — not topic data, so this does not bypass MCP.
_STOPWORDS = {
    "i", "a", "an", "the", "to", "of", "in", "on", "for", "and", "or",
    "what", "should", "first", "study", "learn", "about", "want", "review",
    "is", "are", "how", "do", "does", "with", "my", "me", "please", "help",
}


def _extract_keywords(question: str) -> list[str]:
    """Pull out lowercase, punctuation-free candidate keywords from a
    free-text question, dropping common stopwords."""
    words = re.findall(r"[a-zA-Z]+", question.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 2]


async def _find_best_topic(client: Client, question: str) -> dict | None:
    """Use the MCP catalog resource + search_topics tool to find the best
    matching topic for a free-text question. Returns a small search
    result (id, title, summary) or None if nothing matched.
    """
    # 1. Read the read-only catalog resource to know which titles exist.
    catalog_raw = await client.read_resource("topics://catalog")
    import json
    catalog = json.loads(catalog_raw[0].text)["topics"]

    keywords = _extract_keywords(question)

    # 2. Try to match a full topic title against the question's keywords
    #    (best signal: several words of the title appear in the question).
    best_topic = None
    best_score = 0
    for topic in catalog:
        title_words = set(re.findall(r"[a-zA-Z]+", topic["title"].lower()))
        score = len(title_words & set(keywords))
        if score > best_score:
            best_score = score
            best_topic = topic

    if best_topic:
        results = await client.call_tool(
            "search_topics", {"query": best_topic["title"].lower()}
        )
        if results.data:
            return results.data[0]

    # 3. Fallback: try each keyword individually through search_topics.
    for keyword in keywords:
        results = await client.call_tool("search_topics", {"query": keyword})
        if results.data:
            return results.data[0]

    return None


def _format_answer(question: str, topic: dict | None) -> str:
    """Build a short student-facing answer from MCP data only."""
    if topic is None:
        return (
            f"**Question:** {question}\n\n"
            "I couldn't find a matching topic in the current catalog for "
            "this question. Try rephrasing it, or ask about one of the "
            "topics available (e.g. Python decorators, list comprehensions, "
            "JavaScript closures, Flask routing, MongoDB aggregation, "
            "Python WebSockets)."
        )

    lines = [
        f"**Question:** {question}\n",
        f"## Recommended topic: {topic['title']}\n",
        f"**Why it's relevant:** this topic matched your question in the "
        f"MCP server's catalog and search results.\n",
        f"**Summary:** {topic.get('summary', 'N/A')}\n",
    ]

    prerequisites = topic.get("prerequisites")
    if prerequisites:
        lines.append("**Prerequisites:** " + ", ".join(prerequisites) + "\n")

    key_concepts = topic.get("key_concepts")
    if key_concepts:
        lines.append("**Key concepts:**")
        lines.extend(f"- {kc}" for kc in key_concepts)
        lines.append("")

    common_mistakes = topic.get("common_mistakes")
    if common_mistakes:
        lines.append("**Common mistakes to avoid:**")
        lines.extend(f"- {cm}" for cm in common_mistakes)
        lines.append("")

    practice_idea = topic.get("practice_idea")
    if practice_idea:
        lines.append(f"**Practice idea:** {practice_idea}\n")

    return "\n".join(lines)


async def answer_question(question: str) -> str:
    """Connect to the MCP server (as a real subprocess over stdio),
    call search_topics and get_topic_details through it, and return a
    formatted student-facing answer.
    """
    async with Client(SERVER_SCRIPT) as client:
        match = await _find_best_topic(client, question)

        if match is None:
            return _format_answer(question, None)

        details = await client.call_tool(
            "get_topic_details", {"topic_id": match["id"]}
        )

        if "error" in details.data:
            return _format_answer(question, None)

        return _format_answer(question, details.data)


async def main() -> None:
    question = " ".join(sys.argv[1:]) or (
        "I want to study Python decorators. What should I review first?"
    )
    answer = await answer_question(question)
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
