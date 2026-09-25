# Feuille de Route et Backlog (TODO)

Ce document répertorie le statut des contributions en cours d'Antoine Beaubien, les tâches prioritaires et les fonctionnalités futures prévues pour le serveur Google Workspace MCP.

---

## 1. Suivi des Pull Requests Upstream (`taylorwilsdon/google_workspace_mcp`)

| PR | Branche | Titre / Description | Statut |
| :--- | :--- | :--- | :--- |
| **#1146** | `feat-manage-gsheets-named-ranges` | Ajout des outils de gestion des plages nommées (`manage_named_range`). | **Fusionnée** ✅ |
| **#1147** | `feat-manage-gsheets-smart-chips` | Gestion des Smart Chips dans Google Sheets (`insert_smart_chips`). | **Fusionnée** ✅ |
| **#1148** | `fix-gsheets-typing-and-uv-lock` | Améliorations de typage et alignement `uv.lock`. | **Ouverte** 🔄 |
| **#1173** | `feat-read-sheet-dimensions` | Ajout de l'outil `read_sheet_dimensions` (largeurs de colonnes et hauteurs de lignes). | **Draft (CI 100% verte)** 🟢 |
| **#1175** | `feat-merge-unmerge-cells` | Ajout des capacités de fusion/défusion (`merge_cells`, `merge_type`) dans `format_sheet_range`. | **Draft (CI 100% verte)** 🟢 |

---

## 2. Actions Prioritaires Immédiates

### Finalisation des PRs Upstream
- [ ] Passer la PR **#1173** (`feat-read-sheet-dimensions`) de mode *Draft* à *Ready for Review* dès accord de l'utilisateur.
- [ ] Passer la PR **#1175** (`feat-merge-unmerge-cells`) de mode *Draft* à *Ready for Review* dès accord de l'utilisateur.
- [ ] Répondre aux éventuels retours de revue du mainteneur Taylor Wilsdon.

### Automatisation du Classeur `Courriels (AB)` (`1sS29EksTE-qJSV18kyfY2S_ye0Rv8_q_7rBaUkaTOIQ`)
- [x] Fusionner les cellules `J3:L3` (Titre « Destinataire ») sur la feuille `Courriels (A@B.QC)`.
- [ ] Automatiser le remplissage des formules d'extraction pour les colonnes `J` (Prénom), `K` (Nom), et `L` (Courriel) pour la colonne `Destinataire`.
- [ ] Propager les largeurs et formats de colonnes vers les feuilles `Courriels (AB @gMail)` et `Courriels (HM @)` à l'aide de `read_sheet_dimensions` et `resize_sheet_dimensions`.

---

## 3. Backlog de Fonctionnalités MCP (Google Sheets)

### Manipulation Avancée de Cellules et Dimensions
- [ ] **Outil `get_merged_ranges` :**
  - Permettre la lecture et l'inspection de toutes les cellules fusionnées dans une feuille donnée.
- [ ] **Outil `manage_cell_borders` :**
  - Définir les styles, épaisseurs et couleurs des bordures de cellules (haut, bas, gauche, droite, intérieur).
- [ ] **Outil `insert_delete_dimensions` :**
  - Insérer ou supprimer des lignes et des colonnes sans devoir écraser toute la feuille.
- [ ] **Outil `set_dimension_visibility` :**
  - Masquer (`hide`) ou afficher (`unhide`) explicitement des lignes ou des colonnes spécifiques via l'API Sheets.

---

## 4. Maintenance et Qualité Continue

- [x] Intégrer la règle de préservation stricte de `uv.lock` dans `GEMINI.md` et `ia/AGENTS.md`.
- [x] Standardiser le contrôle de formatage avec `uvx ruff@0.15.22` avant tout commit de fonctionnalité.
- [ ] Maintenir la documentation du guide d'utilisation (`skills/managing-google-workspace/references/`) à jour pour chaque nouvel outil.
- [ ] Conserver `main-ab` comme branche de référence locale opérationnelle agrégeant toutes les fonctionnalités.
