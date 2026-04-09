---
name: import-vault
description: Adopte un vault Obsidian existant dans xais-brain sans casser sa structure. Scanne les dossiers, demande quel dossier joue quel rôle (inbox, daily, projects, research, archive), écrit vault-config.json avec le mapping, et génère un CLAUDE.md adapté. Utiliser pour import-vault, adopter mon vault, utiliser un vault existant, j'ai déjà un vault.
user-invocable: true
disable-model-invocation: true
model: sonnet
---

# import-vault

Bring Your Own Vault — installe xais-brain sur un vault Obsidian existant, sans toucher à la structure.

## Pré-requis

- L'utilisateur a lancé `claude` depuis la racine de son vault existant.
- Un dossier `.obsidian/` est présent (sinon warning).

## Phase 1 : Scan

1. Lister les dossiers top-level (exclure `.obsidian`, `.git`, `.claude`, `.trash`, `node_modules`).
2. Pour chaque dossier, compter les `.md` et détecter des signaux :
   - Fichiers au format date `YYYY-MM-DD*.md` → candidat daily.
   - Sous-dossiers avec CLAUDE.md ou README.md → candidat projects.
   - Nom contenant « inbox », « boîte », « à trier » → candidat inbox.
3. Afficher un résumé :

```
Scan du vault terminé.

342 notes dans 6 dossiers :
  00_Inbox/       → 15 notes (nom = « inbox »)
  01_Projects/    → 45 notes (sous-dossiers détectés)
  02_Areas/       → 23 notes
  03_Resources/   → 87 notes
  04_Archive/     → 67 notes (nom = « archive »)
  Daily/          → 180 notes (dates détectées)
```

## Phase 2 : Mapping interactif (AskUserQuestion)

Pour chacun des 5 rôles xais-brain, poser **une question** (une seule AskUserQuestion avec 5 items) :

- Quel dossier contient tes **notes du jour** ? (candidats détectés + « aucun, crée-le » + « skip »)
- Quel dossier contient tes **projets actifs** ?
- Quel dossier contient tes **recherches / notes permanentes** ?
- Quel dossier contient tes **archives** ?
- Quel dossier contient ta **boîte d'entrée** (fichiers à trier) ?

Note : `memory/` n'est pas dans le mapping — on le crée systématiquement car c'est une convention xais-brain (il n'existe pas dans les autres systèmes PKM).

## Phase 3 : Préférences

Poser les 4 questions de `/vault-setup` (nom, priorités, pro/perso, etc.). Si un `CLAUDE.md` existe déjà, proposer de le merger plutôt que l'écraser.

## Phase 4 : Écriture

1. Créer `vault-config.json` à la racine avec :
   - `adoptedVault: true`
   - `folders: { inbox: "00_Inbox", daily: "Daily", ... }` (mapping user)
   - Préférences de la phase 3.

2. Créer `memory/` et `memory/README.md` si absents (silencieusement).

3. Écrire ou merger `CLAUDE.md` :
   - Si absent → template xais-brain avec la structure user (dossiers remappés).
   - Si présent → backup en `CLAUDE.md.backup-YYYY-MM-DD-HHMMSS`, puis génère un nouveau CLAUDE.md qui importe l'ancien via `@import CLAUDE.md.backup-...` (l'user peut fusionner à la main plus tard).

4. Créer `.claude/skills/`, `.claude/hooks/`, `.claude/rules/`, `.claude/settings.json` (structure xais-brain).

5. Installer les 8 skills et 2 hooks dans `.claude/` (copie depuis `~/.claude/skills/` si ils y sont déjà, sinon demander à l'user de relancer `setup.sh` avec `VAULT_PATH=.`).

## Phase 5 : Validation

- Lire `vault-config.json` pour vérifier que le JSON est valide.
- Vérifier que tous les dossiers mappés existent.
- Afficher un résumé :

```
✓ Vault adopté sans toucher à ta structure.

Mapping :
  inbox    → 00_Inbox/
  daily    → Daily/
  projects → 01_Projects/
  research → 03_Resources/
  archive  → 04_Archive/

Créé :
  ✓ vault-config.json
  ✓ memory/ (nouveau)
  ✓ CLAUDE.md (ton ancien : CLAUDE.md.backup-...)
  ✓ .claude/ (skills, hooks, settings)

Prochaines étapes :
  → /daily pour démarrer ta journée
  → /inbox-zero pour trier 00_Inbox
```

## Cas d'erreur

- **Pas de `.obsidian/`** : warning « Ce dossier ne ressemble pas à un vault Obsidian, continuer quand même ? ».
- **Déjà adopté** (`vault-config.json` existe avec `adoptedVault: true`) : demander « regénérer la config ? ».
- **Aucun candidat détecté** pour un rôle : proposer de créer le dossier avec le nom standard (`inbox/`, `daily/`, etc.).
- **Vault vide** (pas de `.md`) : warning, suggère `/vault-setup` à la place.
