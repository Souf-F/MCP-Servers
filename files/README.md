# MCP Servers in Python: Tools, Resources, and Agent Integration

Projet Holberton School — construction d'un serveur MCP (Model Context Protocol) avec FastMCP, exposant un petit dataset de sujets de programmation, et d'un client/agent qui s'y connecte pour répondre à des questions d'étudiants.

## Structure du projet

```
mcp-intro/
├── server/
│   ├── learning_server.py   # Serveur FastMCP (tools + resource)
│   └── __init__.py
├── client/
│   ├── mcp_client.py        # Client MCP générique
│   ├── agent.py             # Agent qui consomme le serveur MCP
│   └── __init__.py
├── data/
│   └── topics.json          # Dataset local des sujets de programmation
├── output/
│   └── sample_agent_response.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Statut

- [x] Structure du projet créée (Task 0)
- [ ] Serveur MCP fonctionnel avec au moins 2 tools (Task 1+)
- [ ] Au moins 1 resource MCP en lecture seule
- [ ] Client/agent connecté au serveur
- [ ] Documentation d'installation et de test
- [ ] Documentation des tools et resources exposés
- [ ] Section sur l'évaluation des serveurs MCP tiers

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Lancer le serveur

_À compléter dans les tâches suivantes._

## Tester le serveur

_À compléter (MCP Inspector / Insomnia)._

## Évaluer un serveur MCP tiers

_À compléter dans la tâche dédiée._
