# Sample Agent Response

This is a real output produced by `client/agent.py`, which connects to
`server/learning_server.py` as an external subprocess over stdio (MCP
protocol), calls `search_topics` then `get_topic_details` through that
connection, and formats the answer below entirely from the data
returned by the MCP server.

## How to reproduce

```bash
python3 client/agent.py "I want to study Python decorators. What should I review first?"
```

## Question

> I want to study Python decorators. What should I review first?

## Agent answer (actual output, captured on 2026-07-09)

**Question:** I want to study Python decorators. What should I review first?

## Recommended topic: Python Decorators

**Why it's relevant:** this topic matched your question in the MCP server's catalog and search results.

**Summary:** Functions that wrap other functions to extend or modify their behavior without changing their source code.

**Prerequisites:** Functions, Scope, First-class functions

**Key concepts:**
- Higher-order functions
- Wrapper functions
- The @decorator syntax
- functools.wraps

**Common mistakes to avoid:**
- Forgetting to return the wrapper function
- Forgetting to use functools.wraps, losing the original function's metadata
- Confusing decorators with plain function calls

**Practice idea:** Create a decorator that logs the name and execution time of any function it wraps.