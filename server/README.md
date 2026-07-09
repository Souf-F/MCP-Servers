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
- [x] Section MCP Architecture Summary dans le README (Task 1)
- [x] Serveur FastMCP minimal qui démarre (Task 2)
- [x] Dataset local topics.json avec 6 sujets (Task 3)
- [x] Tool search_topics (Task 4)
- [x] Tool get_topic_details (Task 5)
- [ ] Au moins 1 resource MCP en lecture seule
- [ ] Client/agent connecté au serveur
- [ ] Documentation des tools et resources exposés
- [ ] Section sur l'évaluation des serveurs MCP tiers

## MCP Architecture Summary

**Model Context Protocol (MCP)** est un protocole standard qui permet à une application IA de se connecter à des capacités externes (données, outils, fonctions) sans avoir à coder une intégration sur-mesure pour chaque service. C'est un peu l'équivalent d'une prise USB pour les agents IA : le format de connexion est le même, peu importe ce qu'il y a de l'autre côté.

Trois rôles principaux :

- **MCP Host** : l'application IA elle-même (par exemple un agent, un chatbot, un IDE assisté par IA). C'est elle qui pilote la conversation et décide quand aller chercher de l'information externe.
- **MCP Client** : le composant technique qui gère la connexion avec *un* serveur MCP précis. Un host peut créer plusieurs clients s'il veut parler à plusieurs serveurs en même temps (un pour les fichiers, un pour une base de données, etc.).
- **MCP Server** : le programme qui expose des capacités (tools, resources, prompts) que le client peut découvrir et utiliser. Dans ce projet, `learning_server.py` est le serveur.

**Tools vs Resources** :

- Un **tool** est une action que le serveur peut exécuter à la demande du client — typiquement une fonction avec des paramètres, qui peut avoir un effet ou renvoyer un résultat calculé (ex : `search_topics("decorators")`, `suggest_practice("python-decorators")`).
- Une **resource** est une donnée en lecture seule que le serveur met à disposition, consultable directement sans forcément passer par une logique complexe (ex : le catalogue complet des sujets, exposé tel quel).

**Exemple concret dans ce projet** : quand un étudiant demande *"Je veux étudier les décorateurs Python, par quoi je commence ?"*, l'agent (host) passe par son client MCP pour interroger le `learning_server` : il appelle le tool `get_topic("python-decorators")` pour récupérer les prérequis et le résumé, puis éventuellement `suggest_practice(...)` pour une activité pratique. Il peut aussi lire directement la resource du catalogue pour savoir quels sujets existent avant de chercher.

**Pourquoi limiter les capacités exposées** : un serveur MCP ne devrait exposer que le strict nécessaire, car chaque tool ou resource ajouté est une surface d'action supplémentaire que l'agent (ou un attaquant qui détournerait l'agent) peut invoquer. Moins il y a de capacités inutiles, moins il y a de risques d'usage abusif, d'erreurs, ou de fuite de données — un principe proche du *moindre privilège* qu'on retrouve en sécurité.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Nécessite **Python 3.10+** (requis par FastMCP).

## Lancer le serveur

```bash
python3 server/learning_server.py
```

Le serveur démarre avec le transport **stdio** par défaut (utilisé par des clients comme MCP Inspector). Il tourne en attendant des connexions, il n'y a pas de sortie continue dans le terminal — c'est normal.

Pour l'arrêter : `Ctrl+C`.

## Tools et Resources exposés

### `search_topics(query: str) -> list[dict]`
Recherche des sujets par titre ou par concept-clé (`key_concepts`), insensible à la casse. Retourne une liste de résumés courts (`id`, `title`, `summary`) — pas le sujet complet, pour laisser un résultat léger que l'agent peut parcourir avant d'aller chercher les détails. Retourne une liste vide si rien ne correspond ou si la requête est vide.

Exemple : `search_topics("decorator")` retourne `python-decorators` (titre) et `flask-routing` (car son `key_concepts` contient `"@app.route decorator"`).

### `get_topic_details(topic_id: str) -> dict`
Retourne la fiche complète d'un sujet (résumé, prérequis, concepts-clés, erreurs fréquentes, idée de pratique) à partir de son `id` exact. Si l'id n'existe pas, retourne `{"error": "..."}` au lieu de planter.

## Tester le serveur

Test manuel rapide avec un client MCP en mémoire (sans passer par stdio) :

```python
import asyncio
from fastmcp import Client
from server.learning_server import mcp

async def main():
    async with Client(mcp) as client:
        print(await client.list_tools())
        print(await client.call_tool("search_topics", {"query": "decorator"}))
        print(await client.call_tool("get_topic_details", {"topic_id": "python-decorators"}))

asyncio.run(main())
```

Test via l'outil officiel (MCP Inspector) :

```bash
npx @modelcontextprotocol/inspector python3 server/learning_server.py
```

## Évaluer un serveur MCP tiers

_À compléter dans la tâche dédiée._