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
- [x] Resource topics://catalog (Task 6)
- [x] Serveur testé de bout en bout via client/mcp_client.py (Task 7)
- [x] Agent connecté au serveur via MCP, sortie sauvegardée (Task 8)
- [x] Revue d'un serveur MCP tiers (Task 9)
- [x] Documentation des tools et resources exposés

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

### Resource `topics://catalog`
Resource **en lecture seule** (elle ne modifie jamais `data/topics.json`). Retourne un JSON compact avec uniquement `id` et `title` de chaque sujet, pour permettre à un client de parcourir le catalogue disponible avant d'appeler `search_topics` ou `get_topic_details`.

Exemple de retour : `{"topics": [{"id": "python-decorators", "title": "Python Decorators"}, ...]}`

## Tester le serveur

Le serveur est testé via `client/mcp_client.py`, un script FastMCP qui se connecte au serveur **en mémoire** (pas besoin de le lancer dans un process séparé) et vérifie :

- le serveur démarre et liste bien ses tools et sa resource,
- `search_topics` avec une requête valide,
- `search_topics` avec une requête qui ne matche rien (cas d'erreur),
- `get_topic_details` avec un id valide,
- `get_topic_details` avec un id invalide (cas d'erreur),
- la lecture de la resource `topics://catalog`.

Lancer le test depuis la racine du projet :

```bash
python3 client/mcp_client.py
```

**Sortie réelle obtenue :**

```
Tools disponibles: ['search_topics', 'get_topic_details']
Resources disponibles: ['topics://catalog']

--- search_topics('decorator') ---
[{'id': 'python-decorators', 'title': 'Python Decorators', 'summary': '...'},
 {'id': 'flask-routing', 'title': 'Flask Routing and Views', 'summary': '...'}]

--- search_topics('nonexistent_topic_xyz') ---
[]

--- get_topic_details('python-decorators') ---
{'id': 'python-decorators', 'title': 'Python Decorators', ...
 'prerequisites': ['Functions', 'Scope', 'First-class functions'], ...}

--- get_topic_details('does-not-exist') ---
{'error': "No topic found with id 'does-not-exist'."}

--- read topics://catalog ---
{"topics": [{"id": "python-decorators", "title": "Python Decorators"}, ...]}
```

Alternative avec l'outil officiel MCP Inspector (interface web) :

```bash
npx @modelcontextprotocol/inspector python3 server/learning_server.py
```

## Agent

`client/agent.py` est un agent déterministe (pas de LLM) : il reçoit une question d'étudiant en texte libre, se connecte au serveur MCP **comme un vrai sous-processus séparé** (via stdio, pas d'import direct des fonctions du serveur), appelle `search_topics` puis `get_topic_details` à travers cette connexion MCP, et formate une réponse uniquement à partir des données renvoyées par le serveur.

Fonctionnement :
1. Lit la resource `topics://catalog` pour connaître les titres disponibles.
2. Extrait des mots-clés de la question (en ignorant les mots vides comme "the", "what", "study"...).
3. Cherche le titre du catalogue qui correspond le mieux à ces mots-clés, puis appelle `search_topics` avec ce titre.
4. Si rien ne matche, retente `search_topics` mot-clé par mot-clé.
5. Appelle `get_topic_details` sur le premier résultat trouvé pour récupérer la fiche complète.
6. Formate une réponse avec : sujet recommandé, résumé, prérequis, concepts-clés, erreurs fréquentes, idée de pratique.
7. Si aucun sujet ne correspond, le dit clairement plutôt que d'inventer une réponse.

Lancer l'agent :

```bash
python3 client/agent.py "I want to study Python decorators. What should I review first?"
```

(sans argument, une question par défaut est utilisée)

Un exemple réel de sortie est sauvegardé dans [`output/sample_agent_response.md`](output/sample_agent_response.md).

## Évaluer un serveur MCP tiers

Serveur choisi : **Filesystem MCP Server**, le serveur de référence officiel publié par l'équipe Model Context Protocol (paquet npm `@modelcontextprotocol/server-filesystem`, dépôt GitHub `modelcontextprotocol/servers`). Choix volontairement low-risk : c'est un serveur officiel, open-source, largement utilisé (plus de 230 000 téléchargements hebdomadaires sur npm), et son fonctionnement est simple à auditer.

**1. Ce que fait le serveur**
Il expose des opérations sur le système de fichiers local : lire des fichiers, en écrire/modifier, créer des dossiers, lister le contenu d'un répertoire, déplacer des fichiers, chercher des fichiers par nom, et récupérer les métadonnées d'un fichier (taille, dates de création/modification...).

**2. Local ou distant**
Il tourne **localement**, en sous-processus sur la machine de l'utilisateur (lancé via `npx` ou dans un conteneur Docker), et communique avec le client par stdio. Il n'expose rien sur le réseau par défaut.

**3. Tools / resources exposés**
Des tools comme `read_file`, `write_file`, `edit_file`, `create_directory`, `list_directory`, `move_file`, `search_files`, `get_file_info`. Chaque tool est explicitement annoté "lecture seule" ou "capable d'écrire", ce qui permet à un client MCP de distinguer les opérations sûres des opérations potentiellement destructrices.

**4. Permissions / credentials requis**
Pas de token ni de compte à fournir. La sécurité repose uniquement sur une **liste de répertoires autorisés**, passée en argument au démarrage du serveur (ex : `npx @modelcontextprotocol/server-filesystem /Users/moi/Desktop`). Le serveur refuse toute opération en dehors de ces répertoires. Il tourne avec les permissions du compte utilisateur qui le lance : il peut donc faire tout ce que cet utilisateur peut faire manuellement, mais seulement dans le périmètre autorisé.

**5. Un risque**
Si on autorise un répertoire trop large (par exemple tout le dossier utilisateur au lieu d'un sous-dossier précis), un agent mal guidé — ou un prompt injection glissé dans un fichier lu par l'agent — pourrait lire ou écraser des fichiers sensibles (identifiants, configs, documents personnels) qui n'ont rien à voir avec la tâche demandée.

**6. Une mesure de sécurité à appliquer**
Toujours limiter l'accès à un **sous-dossier de projet dédié et minimal**, jamais au dossier utilisateur entier ni à la racine du disque, et lancer le serveur en lecture seule (option `ro` en Docker) quand aucune écriture n'est nécessaire. C'est le même principe de moindre privilège déjà évoqué dans la section MCP Architecture Summary.

**Sources consultées** : [dépôt GitHub `modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers), [page npm du paquet](https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem), [documentation officielle "Connect to local MCP servers"](https://modelcontextprotocol.io/docs/develop/connect-local-servers).