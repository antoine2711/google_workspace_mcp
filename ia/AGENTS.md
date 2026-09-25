# Directives et Instructions pour les Agents IA

Ce document contient les directives fondamentales, les principes d'automatisation, et les règles architecturales à respecter rigoureusement lors de toute intervention sur le projet `google_workspace_mcp`.
Site internet : https://workspacemcp.com/


---

## 1. Principes Fondamentaux d'Automatisation

- **100 % Automatisé – Zéro intervention manuelle :**
  - **Ne jamais proposer de manipulations manuelles dans l'interface graphique (GUI)** (ex. : ne jamais dire à l'utilisateur de cliquer dans Google Sheets pour fusionner des cellules, redimensionner des colonnes ou formater des données).
  - L'utilisateur maîtrise déjà parfaitement les manipulations manuelles ; son objectif absolu est d'automatiser chaque action via le code ou les outils MCP.
- **Ajout d'outils MCP au lieu de scripts jetables (ad-hoc) :**
  - Lorsqu'une fonctionnalité n'existe pas dans le serveur MCP (par exemple : lecture des dimensions d'une feuille, fusion de cellules), **ne jamais écrire de scripts Python ad-hoc contournant le serveur MCP** ou lisant manuellement les jetons OAuth dans les fichiers de credentials.
  - **Toujours développer la fonctionnalité directement dans le code du serveur MCP**, l'exposer en tant qu'outil `@server.tool`, la tester unitairement, et la fusionner pour une utilisation propre et pérenne.

---

## 2. Architecture des Branches Git

Le projet repose sur une séparation stricte des rôles entre les branches :

1. **`main` (Branche miroir upstream) :**
   - Doit rester **strictement identique** à la branche `main` du dépôt officiel amont (`taylorwilsdon/google_workspace_mcp`).
   - Ne jamais y pousser de commits locaux ou de fonctionnalités non encore fusionnées en amont.
2. **`main-ab` (Branche d'exécution personnelle d'Antoine) :**
   - Branche centrale pour l'environnement personnel d'Antoine.
   - Intègre toutes les fonctionnalités développées, testées et validées (`feat-*`), ainsi que les correctifs spécifiques.
   - C'est **cette branche qui est exécutée** par Antigravity et le client MCP local via `~/.gemini/config/mcp_config.json`.
   - La copie de travail locale doit rester positionnée sur `main-ab` en dehors des phases d'édition de branches spécifiques.
3. **`feat-<nom-de-fonctionnalité>` (Branches de fonctionnalités) :**
   - Toujours branchées à partir de `main` (à jour avec `upstream/main`).
   - Dédiées à une fonctionnalité ou un correctif unique.
   - Doivent faire l'objet d'une **Draft Pull Request (PR en mode brouillon)** sur GitHub amont (`taylorwilsdon/google_workspace_mcp`).
4. **`ia` (Branche des directives IA) :**
   - Dédiée à la documentation, aux directives et aux feuilles de route destinées à l'intelligence artificielle travaillant sur ce dépôt (`AGENTS.md`, `ARCHITECTURE.md`, `TODO.md`).

---

## 3. Règle Stricte sur le Fichier de Verrouillage (`uv.lock`)

- **Préservation absolue de `uv.lock` :**
  - Le fichier `uv.lock` **ne doit jamais être modifié ni inclus dans les commits** des branches de fonctionnalités (`feat-*`), sauf demande explicite ou branche dédiée aux dépendances.
  - Avant de commiter ou de pousser une branche `feat-*`, vérifier systématiquement :
    ```bash
    git diff main..<branche> -- uv.lock
    ```
    Cette commande doit impérativement retourner un diff vide.
  - En cas de modification accidentelle lors de tests ou de l'installation de paquets, restaurer immédiatement le fichier :
    ```bash
    git checkout main -- uv.lock
    ```

---

## 4. Standards de Qualité de Code, Tests et Formatage

- **Formatage et Linting avec Ruff (Strict) :**
  - La CI amont utilise la version épinglée `0.15.22`.
  - Toujours valider avant commit :
    ```bash
    uvx ruff@0.15.22 check
    uvx ruff@0.15.22 format --check
    ```
  - Appliquer le formatage si nécessaire :
    ```bash
    uvx ruff@0.15.22 format
    ```
- **Tests Unitaires Obligatoires :**
  - Toute nouvelle fonctionnalité doit s'accompagner d'une suite complète de tests unitaires dans `tests/<service>/`.
  - Mocker systématiquement les appels aux API Google (aucune dépendance réseau dans les tests unitaires).
  - Couvrir les cas nominaux, les valeurs par défaut, et les cas d'erreur (`UserInputError`, arguments invalides).
  - Lancer les tests avec `uv run pytest tests/<service>/test_<nom>.py`.
- **Documentation et Typage :**
  - Respecter les docstrings Google (`Args:`, `Returns:`, `Raises:`).
  - Maintenir un typage strict et clair.
  - Documenter les nouveaux outils dans le guide de compétences : `skills/managing-google-workspace/references/<service>.md`.

---

## 5. Format des Pull Requests Upstream

- Toujours ouvrir les PRs en mode **Draft** (`--draft`).
- Utiliser le format de description standardisé d'Antoine (contexte, changements, tests, documentation, impact).
