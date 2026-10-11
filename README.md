# MCP Servers — Programming Learning Server

MCP server built with FastMCP exposing a programming topic dataset. A connected agent answers student questions like *"What should I study first about Python decorators?"*

Holberton School project — Model Context Protocol, Tasks 7 & 8.

## Architecture

```
Student question
      │
      ▼
┌─────────────┐    stdio / MCP    ┌───────────────────────┐
│  agent.py   │ ─────────────────► │  learning_server.py   │
│  (client)   │ ◄───────────────── │  (FastMCP server)     │
└─────────────┘                    └──────────┬────────────┘
                                              │
                                      data/topics.json
                                      (6 programming topics)
```

## Exposed capabilities

| Type | Name | Description |
|------|------|-------------|
| Tool |  | Search by title or key concept |
| Tool |  | Full topic record — prerequisites, concepts, practice |
| Resource |  | Read-only catalog of all available topics |

## Topics available

Python Decorators · Python Closures · Flask Routing · MongoDB Aggregation · JavaScript Closures · WebSockets

## What is MCP?

Model Context Protocol standardizes how an AI connects to external capabilities (data, tools, APIs) — same plug format regardless of what's on the other side.

```
Host    — the AI app driving the conversation
Client  — manages one MCP connection
Server  — exposes tools and resources the client can call
```

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r server/requirements.txt
```

## Run

```bash
# Start the server
python3 server/learning_server.py

# Test the server (separate terminal)
python3 server/mcp_client.py

# Run the agent
python3 server/agent.py "I want to study Python decorators. What should I review first?"
```

## Structure

```
├── server/
│   ├── learning_server.py   # FastMCP server (2 tools + 1 resource)
│   ├── mcp_client.py        # Test client
│   ├── agent.py             # Deterministic student agent
│   └── requirements.txt
└── data/
    └── topics.json          # 6 programming topics
```

---

Soufiane Filali · Holberton School France
