# MCP Servers in Python

Projet Holberton School — construction d'un serveur MCP (Model Context Protocol) avec FastMCP, exposant un petit dataset de sujets de programmation, et d'un agent qui s'y connecte pour répondre à des questions d'étudiants.

## Description

Ce projet implémente un **Programming Learning MCP Server** : un serveur MCP local qui expose un petit dataset de sujets de programmation (Python decorators, closures JS, routing Flask, agrégation MongoDB, WebSockets...) via deux tools et une resource en lecture seule. Un agent déterministe (`client/agent.py`) se connecte à ce serveur comme un vrai sous-processus externe (stdio) — sans jamais importer directement les fonctions du serveur — pour répondre à des questions d'étudiants du type *"Je veux étudier les décorateurs Python, par quoi je commence ?"*.

```
mcp-intro/
├── server/
│   ├── learning_server.py   # Serveur FastMCP (2 tools + 1 resource)
│   └── __init__.py
├── client/
│   ├── mcp_client.py        # Script de test du serveur (Task 7)
│   ├── agent.py             # Agent qui consomme le serveur MCP (Task 8)
│   └── __init__.py
├── data/
│   └── topics.json          # Dataset local (6 sujets)
├── output/
│   └── sample_agent_response.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## MCP Architecture Summary

**Model Context Protocol (MCP)** est un protocole standard qui permet à une application IA de se connecter à des capacités externes (données, outils, fonctions) sans avoir à coder une intégration sur-mesure pour chaque service. C'est un peu l'équivalent d'une prise USB pour les agents IA : le format de connexion est le même, peu importe ce qu'il y a de l'autre côté.

Trois rôles principaux :

- **MCP Host** : l'application IA elle-même (par exemple un agent, un chatbot, un IDE assisté par IA). C'est elle qui pilote la conversation et décide quand aller chercher de l'information externe.
- **MCP Client** : le composant technique qui gère la connexion avec *un* serveur MCP précis. Un host peut créer plusieurs clients s'il veut parler à plusieurs serveurs en même temps (un pour les fichiers, un pour une base de données, etc.).
- **MCP Server** : le programme qui expose des capacités (tools, resources, prompts) que le client peut découvrir et utiliser. Dans ce projet, `learning_server.py` est le serveur.

**Tools vs Resources** :

- Un **tool** est une action que le serveur peut exécuter à la demande du client — typiquement une fonction avec des paramètres, qui peut avoir un effet ou renvoyer un résultat calculé (ex : `search_topics("decorators")`, `get_topic_details("python-decorators")`).
- Une **resource** est une donnée en lecture seule que le serveur met à disposition, consultable directement sans forcément passer par une logique complexe (ex : le catalogue complet des sujets, exposé tel quel).

**Exemple concret dans ce projet** : quand un étudiant demande *"Je veux étudier les décorateurs Python, par quoi je commence ?"*, l'agent (host) passe par son client MCP pour interroger le `learning_server` : il appelle le tool `get_topic_details("python-decorators")` pour récupérer les prérequis et le résumé, puis peut lire la resource du catalogue pour savoir quels sujets existent avant de chercher.

**Pourquoi limiter les capacités exposées** : un serveur MCP ne devrait exposer que le strict nécessaire, car chaque tool ou resource ajouté est une surface d'action supplémentaire que l'agent (ou un attaquant qui détournerait l'agent) peut invoquer. Moins il y a de capacités inutiles, moins il y a de risques d'usage abusif, d'erreurs, ou de fuite de données — un principe proche du *moindre privilège* qu'on retrouve en sécurité.

## Requirements

- **Python 3.10+** (requis par FastMCP)
- Node.js + `npx` (uniquement si tu veux utiliser MCP Inspector)
- Dépendances Python listées dans `requirements.txt` (`fastmcp`, `mcp`, `python-dotenv`)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## How to Run the Server

Depuis la racine du projet :

```bash
python3 server/learning_server.py
```

Le serveur démarre avec le transport **stdio** par défaut. Il tourne en attendant des connexions — pas de sortie continue dans le terminal, c'est normal. Ne tape rien au clavier dans ce terminal une fois lancé (le serveur essaierait de parser ton texte comme un message JSON-RPC et renverrait une erreur de parsing).

Pour l'arrêter : `Ctrl+C`.

## How to Test the Server

Le serveur est testé via `client/mcp_client.py`, un script FastMCP qui se connecte au serveur **en mémoire** et vérifie :

- le serveur démarre et liste bien ses tools et sa resource,
- `search_topics` avec une requête valide,
- `search_topics` avec une requête qui ne matche rien (cas d'erreur),
- `get_topic_details` avec un id valide,
- `get_topic_details` avec un id invalide (cas d'erreur),
- la lecture de la resource `topics://catalog`.

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

## How to Run the Agent

`client/agent.py` reçoit une question d'étudiant en texte libre, se connecte au serveur MCP **comme un vrai sous-processus séparé** (stdio), appelle `search_topics` puis `get_topic_details` à travers cette connexion MCP, et formate une réponse uniquement à partir des données renvoyées par le serveur.

```bash
python3 client/agent.py "I want to study Python decorators. What should I review first?"
```

(sans argument, une question par défaut est utilisée)

Fonctionnement interne :
1. Lit la resource `topics://catalog` pour connaître les titres disponibles.
2. Extrait des mots-clés de la question (en ignorant les mots vides comme "the", "what", "study"...).
3. Cherche le titre du catalogue qui correspond le mieux, puis appelle `search_topics` avec ce titre.
4. Si rien ne matche, retente `search_topics` mot-clé par mot-clé.
5. Appelle `get_topic_details` sur le premier résultat trouvé.
6. Formate la réponse (sujet recommandé, résumé, prérequis, concepts-clés, erreurs fréquentes, idée de pratique).
7. Si aucun sujet ne correspond, le dit clairement plutôt que d'inventer une réponse.

## Available Tools

### `search_topics(query: str) -> list[dict]`
Recherche des sujets par titre ou par concept-clé (`key_concepts`), insensible à la casse. Retourne une liste de résumés courts (`id`, `title`, `summary`). Retourne une liste vide si rien ne correspond ou si la requête est vide.

Exemple : `search_topics("decorator")` retourne `python-decorators` (titre) et `flask-routing` (car son `key_concepts` contient `"@app.route decorator"`).

### `get_topic_details(topic_id: str) -> dict`
Retourne la fiche complète d'un sujet (résumé, prérequis, concepts-clés, erreurs fréquentes, idée de pratique) à partir de son `id` exact. Si l'id n'existe pas, retourne `{"error": "..."}` au lieu de planter.

## Available Resources

### `topics://catalog`
Resource **en lecture seule** (elle ne modifie jamais `data/topics.json`). Retourne un JSON compact avec uniquement `id` et `title` de chaque sujet, pour permettre à un client de parcourir le catalogue disponible avant d'appeler les tools.

Exemple de retour : `{"topics": [{"id": "python-decorators", "title": "Python Decorators"}, ...]}`

## Third-Party MCP Server Review

Serveur choisi : **Filesystem MCP Server**, le serveur de référence officiel publié par l'équipe Model Context Protocol (paquet npm `@modelcontextprotocol/server-filesystem`, dépôt GitHub `modelcontextprotocol/servers`). Choix volontairement low-risk : c'est un serveur officiel, open-source, largement utilisé (plus de 230 000 téléchargements hebdomadaires sur npm), et son fonctionnement est simple à auditer.

**1. Ce que fait le serveur**
Il expose des opérations sur le système de fichiers local : lire des fichiers, en écrire/modifier, créer des dossiers, lister le contenu d'un répertoire, déplacer des fichiers, chercher des fichiers par nom, et récupérer les métadonnées d'un fichier.

**2. Local ou distant**
Il tourne **localement**, en sous-processus sur la machine de l'utilisateur (lancé via `npx` ou dans un conteneur Docker), et communique avec le client par stdio. Il n'expose rien sur le réseau par défaut.

**3. Tools / resources exposés**
Des tools comme `read_file`, `write_file`, `edit_file`, `create_directory`, `list_directory`, `move_file`, `search_files`, `get_file_info`. Chaque tool est explicitement annoté "lecture seule" ou "capable d'écrire", ce qui permet à un client MCP de distinguer les opérations sûres des opérations potentiellement destructrices.

**4. Permissions / credentials requis**
Pas de token ni de compte à fournir. La sécurité repose uniquement sur une **liste de répertoires autorisés**, passée en argument au démarrage du serveur (ex : `npx @modelcontextprotocol/server-filesystem /Users/moi/Desktop`). Le serveur refuse toute opération en dehors de ces répertoires. Il tourne avec les permissions du compte utilisateur qui le lance.

**5. Un risque**
Si on autorise un répertoire trop large (par exemple tout le dossier utilisateur au lieu d'un sous-dossier précis), un agent mal guidé — ou un prompt injection glissé dans un fichier lu par l'agent — pourrait lire ou écraser des fichiers sensibles qui n'ont rien à voir avec la tâche demandée.

**6. Une mesure de sécurité à appliquer**
Toujours limiter l'accès à un **sous-dossier de projet dédié et minimal**, jamais au dossier utilisateur entier ni à la racine du disque, et lancer le serveur en lecture seule (option `ro` en Docker) quand aucune écriture n'est nécessaire. Même principe de moindre privilège qu'en MCP Architecture Summary.

**Sources consultées** : [dépôt GitHub `modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers), [page npm du paquet](https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem), [documentation officielle "Connect to local MCP servers"](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

## Example Output

Réponse réelle produite par `client/agent.py` (voir aussi [`output/sample_agent_response.md`](output/sample_agent_response.md)) :

> **Question:** I want to study Python decorators. What should I review first?
>
> **Recommended topic:** Python Decorators
>
> **Summary:** Functions that wrap other functions to extend or modify their behavior without changing their source code.
>
> **Prerequisites:** Functions, Scope, First-class functions
>
> **Key concepts:** Higher-order functions, Wrapper functions, The @decorator syntax, functools.wraps
>
> **Common mistakes to avoid:** Forgetting to return the wrapper function; forgetting `functools.wraps`; confusing decorators with plain function calls.
>
> **Practice idea:** Create a decorator that logs the name and execution time of any function it wraps.

## Known Limitations

- **Recherche naïve** : `search_topics` fait un simple test de sous-chaîne (`in`) sur le titre et les `key_concepts`, insensible à la casse mais sans tolérance aux fautes de frappe ni recherche floue (typo-tolerant). Une faute dans la requête ne retournera rien.
- **Extraction de mots-clés basique dans l'agent** : `client/agent.py` utilise une liste de stopwords fixe et un matching mot-à-mot très simple pour deviner le sujet recherché ; une question formulée de façon très détournée (sans les mots du titre ni des concepts-clés) peut ne rien trouver alors qu'un humain aurait compris la question.
- **Dataset minuscule et statique** : seulement 6 sujets dans `data/topics.json`, rechargé à chaque appel de tool (pas de cache) — suffisant pour ce projet pédagogique, pas pour un usage réel à grande échelle.
- **Pas d'authentification** : le serveur ne demande aucune credential et n'a aucune notion d'utilisateur — cohérent avec un projet local de démonstration, mais à ne pas reproduire tel quel pour un serveur exposé publiquement.
- **Agent déterministe, pas de LLM** : `client/agent.py` ne fait aucun raisonnement réel, juste du matching de mots-clés. Il ne comprend pas les questions formulées de façon ambiguë ou avec plusieurs sujets à la fois.
- **Bug rencontré pendant le dev** : au départ `data/topics.json` avait été placé par erreur dans `server/` au lieu de `data/` à la racine — le serveur silencieusement retournait des listes vides (grâce au `try/except` dans `_load_topics()`, qui masque volontairement les erreurs de fichier manquant pour ne pas planter, mais qui a aussi caché ce bug de chemin plus longtemps que prévu).

## Reflection

**1. What problem does MCP solve ?**
Sans MCP, chaque agent IA qui veut accéder à un outil externe (fichiers, base de données, API) doit être connecté avec une intégration sur-mesure, propre à cet outil. MCP standardise ce branchement : un même protocole permet à n'importe quel client MCP de découvrir et utiliser n'importe quel serveur MCP, sans code d'intégration spécifique à chaque paire client/serveur.

**2. What is the difference between an MCP tool and an MCP resource ?**
Un tool est une action/computation invocable avec des paramètres (ex : chercher, calculer, transformer). Une resource est une donnée en lecture seule, identifiée par une URI, consultable directement sans logique complexe. Dans ce projet : `search_topics`/`get_topic_details` sont des tools (ils prennent un paramètre et traitent une requête), `topics://catalog` est une resource (elle renvoie juste l'état actuel du catalogue).

**3. What does your MCP server expose ?**
Deux tools (`search_topics`, `get_topic_details`) et une resource (`topics://catalog`), construits au-dessus d'un dataset local de 6 sujets de programmation stocké dans `data/topics.json`.

**4. How does your agent use the MCP server ?**
`client/agent.py` se connecte au serveur comme un vrai sous-processus externe via `fastmcp.Client("server/learning_server.py")` (transport stdio) — jamais d'import direct des fonctions Python du serveur. Il lit d'abord la resource du catalogue, puis appelle `search_topics` pour trouver un sujet pertinent, puis `get_topic_details` pour récupérer la fiche complète, et construit sa réponse uniquement à partir de ces données MCP.

**5. What should you check before using a third-party MCP server ?**
Ce qu'il expose exactement (tools/resources), s'il tourne en local ou à distance, quelles permissions/credentials il demande, quel est le périmètre d'accès qu'on lui donne (ex : quels répertoires, quelles bases), et si le code est open-source et maintenu par une source fiable (comme le dépôt officiel `modelcontextprotocol/servers` plutôt qu'un fork obscur).

**6. What limitation did you observe in your implementation ?**
La recherche par sous-chaîne de `search_topics` est fragile : une faute de frappe ou une formulation trop éloignée du titre/`key_concepts` du sujet ne retourne rien, même si un humain comprendrait la question. L'agent hérite de cette limite puisqu'il s'appuie sur le même mécanisme de recherche.