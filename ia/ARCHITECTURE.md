# Architecture du Serveur Google Workspace MCP

Ce document détaille l'architecture logicielle, la structure modulaire, le flux d'authentification et les mécanismes d'exécution du serveur MCP `google_workspace_mcp`.

---

## 1. Vue d'Ensemble

Le projet `google_workspace_mcp` est un serveur **Model Context Protocol (MCP)** construit sur la bibliothèque **FastMCP** (Python). Il permet aux agents d'intelligence artificielle (tels qu'Antigravity) d'interagir directement et de façon sécurisée avec l'écosystème Google Workspace (Sheets, Gmail, Drive, Docs, Calendar, Contacts, Chat, Forms, Slides, Tasks, AppScript, Search).

```
┌─────────────────────────────────────────────────────────────┐
│                       Client MCP (ex. Antigravity)          │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON-RPC (stdio)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Serveur FastMCP                          │
│  - fastmcp_server.py / core/server.py                       │
│  - core/tool_registry.py & core/tool_tiers.yaml             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌───────────────────────────────┐ ┌───────────────────────────┐
│        Couche Auth            │ │   Couche Outils Métier    │
│  - auth/google_auth.py        │ │  - gsheets/sheets_tools.py│
│  - auth/service_decorator.py  │ │  - gmail/gmail_tools.py   │
│  - auth/credential_store.py   │ │  - gdrive/drive_tools.py  │
│  - ~/.google_workspace_mcp/   │ │  - gdocs/docs_tools.py    │
└───────────────┬───────────────┘ └─────────────┬─────────────┘
                │                               │
                └──────────────┬────────────────┘
                               │ Appels Google API v4
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Google Workspace REST APIs                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Structure Modulaire du Codebase

| Répertoire / Fichier | Rôle architectural |
| :--- | :--- |
| `core/server.py` | Point d'entrée de l'instance FastMCP, configuration du serveur et instructions. |
| `core/tool_registry.py` | Chargement dynamique des outils, application des filtres de sécurité et des tiers. |
| `core/tool_tiers.yaml` | Définition des paliers d'outils (`core`, `extended`, `complete`). |
| `core/utils.py` | Décorateurs d'erreurs (`@handle_http_errors`), classes d'erreurs (`UserInputError`). |
| `auth/google_auth.py` | Gestion de l'authentification OAuth 2.0, rafraîchissement des tokens et construction des services Google API. |
| `auth/service_decorator.py` | Décorateur `@require_google_service` injectant le client Google authentifié dans les outils. |
| `auth/scopes.py` | Constantes des portées OAuth (lecture seule, écriture, administration). |
| `auth/credential_store.py` | Stockage local et persistance des jetons dans `~/.google_workspace_mcp/credentials`. |
| `gsheets/` | Outils Sheets (`sheets_tools.py`) et fonctions d'aide pour plages A1 et cellules (`sheets_helpers.py`). |
| `gmail/`, `gdrive/`, etc. | Outils spécialisés par produit Google. |
| `skills/` | Documentation des compétences et des références d'outils pour les agents. |
| `tests/` | Suite complète de tests unitaires et d'intégration avec mocks pytest. |

---

## 3. Gestion de l'Authentification et Mode Single-User

### Mode Single-User (`--single-user`)
En environnement local ou sur poste de travail personnel :
- Le serveur est démarré avec l'argument `--single-user`.
- Ce mode contourne le routage multi-utilisateurs et utilise directement les identifiants stockés dans :
  `~/.google_workspace_mcp/credentials/`
- Les variables d'environnement clés sont définies dans `~/.gemini/config/mcp_config.json` :
  - `GOOGLE_OAUTH_CLIENT_ID`
  - `GOOGLE_OAUTH_CLIENT_SECRET`
  - `USER_GOOGLE_EMAIL` (ex. `antoine.beaubien@gmail.com`)
  - `MCP_SINGLE_USER_MODE="1"`

### Cycle d'Authentification d'un Outil
Lorsqu'un outil décoré par `@require_google_service("sheets", "sheets_write")` est appelé :
1. Le décorateur extrait l'email utilisateur (`user_google_email` ou variable d'environnement).
2. `get_authenticated_google_service(...)` charge les identifiants OAuth valides depuis le `credential_store`.
3. Si le token est expiré, il est automatiquement rafraîchi via les APIs Google OAuth.
4. L'objet `Resource` Google API (ex. `sheets.spreadsheets()`) est instancié et injecté en premier paramètre (`service`) de la fonction d'implémentation.

---

## 4. Cycle de Vie d'un Outil MCP

Chaque outil suit un modèle de conception en deux couches :

1. **Fonction d'implémentation interne (`_<nom_outil>_impl`) :**
   - Reçoit le `service` Google API et les paramètres bruts.
   - Contient la logique métier, la validation des paramètres (`UserInputError`) et les appels d'API via `asyncio.to_thread`.
   - Retourne des structures de données Python typées (`dict`, `list`).
   - Permet des tests unitaires rapides et isolés sans passer par le runtime FastMCP.

2. **Fonction d'outil MCP exposée (`@server.tool`) :**
   - Décorée avec `@server.tool`, `@handle_http_errors` et `@require_google_service`.
   - Expose une docstring Google détaillée pour les LLM (description, `Args:`, `Returns:`, `Raises:`).
   - Convertit les résultats en texte clair ou JSON formaté pour le retour MCP.

---

## 5. Workflow d'Ajout d'un Nouvel Outil

Lors de l'ajout d'une fonctionnalité :

1. **Implémentation métier :**
   - Ajouter `_<nom_outil>_impl` dans `<service>/<service>_tools.py`.
   - Ajouter la fonction wrapper `@server.tool(...)`.
2. **Attribution des scopes :**
   - S'assurer que le scope minimal requis est déclaré dans `auth/scopes.py`.
3. **Enregistrement dans les Tiers :**
   - Déclarer le nom de l'outil dans `core/tool_tiers.yaml` (sous `extended` et `complete`).
4. **Tests Unitaires :**
   - Créer ou enrichir `tests/<service>/test_<nom_outil>.py`.
   - Tester avec mocks du service Google (`MagicMock`, `AsyncMock`).
5. **Formatage et Validation :**
   - `uvx ruff@0.15.22 format`
   - `uvx ruff@0.15.22 check`
   - `uv run pytest tests/<service>/`
6. **Documentation :**
   - Ajouter la documentation d'utilisation dans `skills/managing-google-workspace/references/<service>.md`.
