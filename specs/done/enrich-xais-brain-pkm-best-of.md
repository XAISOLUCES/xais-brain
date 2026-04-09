# Enrichir xais-brain avec le best-of des repos PKM de référence

> Plan d'implémentation — porter les meilleures idées de `obsidian-claude-pkm` et `claudesidian` dans `xais-brain`, en restant fidèle à la philosophie one-liner minimaliste FR.

---

## 1. Contexte et objectifs

### Problème

`xais-brain` a un setup solide (6 skills FR, multi-LLM, idempotent, curl|bash) mais manque de plusieurs features qui existent dans les repos PKM concurrents :

- Les skills vivent sous `skills/` à la racine du repo — la convention Claude Code moderne est `.claude/skills/`.
- Aucun hook SessionStart ni UserPromptSubmit → pas de contexte injecté automatiquement en début de session, pas de découverte de skills.
- Pas de commande pour nettoyer le texte AI-ifié (« leverage », « moreover », etc.).
- Pas de parcours BYOV (Bring Your Own Vault) : un utilisateur avec un vault Obsidian existant n'a que `vault-setup` qui suppose la structure standard.
- La config du vault (nom user, préférences, provider LLM) est éparpillée entre `CLAUDE.md` et `.env` — pas de source de vérité structurée lisible par les hooks.
- Le frontmatter des skills est minimaliste (`name` + `description`) — pas de `user-invocable`, `disable-model-invocation`, `model` → pas de garde-fou anti auto-trigger ni de contrôle de modèle.
- Pas d'output style coach FR.

### Résultat attendu

Après ce build, `xais-brain` aura :

1. Tous les skills migrés vers `.claude/skills/` (vault **et** global), avec un setup.sh mis à jour.
2. Deux hooks shell FR (`session-init.sh` qui surface le contexte du jour, `skill-discovery.sh` qui liste les slash commands sur demande).
3. Un skill `/humanise` FR qui dé-IA-ifie un texte (équivalent FR de `de-ai-ify`).
4. Un skill `/import-vault` FR qui scanne un vault Obsidian existant, mappe les dossiers interactivement, et écrit la config (équivalent light de `adopt`).
5. Un `vault-config.json` à la racine du vault comme source de vérité structurée (nom, provider, review day, folder mapping, version).
6. Un frontmatter skills enrichi (`user-invocable`, `disable-model-invocation`, `model`) appliqué aux 6 skills existants + les 2 nouveaux.
7. Un output style `coach.md` en FR activable via `/output-style coach`.

### Non-scope explicite (ne PAS faire)

- **Pas de `/init-bootstrap` 854 lignes** — over-engineered, on garde setup.sh one-liner.
- **Pas de cascade PKM 3Y→Y→M→W→D** — trop structuré, xais-brain reste un vault libre inbox/daily/projects/research/archive/memory.
- **Pas de fichier `FIRST_RUN` ni de cérémonie bootstrap** — le flux est curl|bash → `/vault-setup`, point.
- **Pas d'auto-commit hook** — l'utilisateur versionne à la main si il veut (on n'impose pas git).
- **Pas de cron/schedule**, pas de webhooks, pas d'intégrations externes.
- **Pas de traduction des skills Kepano** (git-worktrees, systematic-debugging, etc.) — ils restent EN, c'est hors scope.

### Contraintes

- **FR-first** : toutes les descriptions, prompts, messages hook, et contenu `coach.md` sont en français. Les noms de fichiers/skills peuvent rester en anglais (convention Claude Code).
- **Idempotent** : `setup.sh` doit rester safe à relancer — il ne casse pas les vaults existants et ne dupplique rien.
- **Compat descendante** : si un utilisateur a déjà un vault xais-brain avec l'ancienne structure `skills/` (hors `.claude/`), le setup détecte et migre sans perte.
- **Pas de dépendance nouvelle** : pas de lib Python ou Node supplémentaire. Bash + Python stdlib pour les hooks.
- **Une seule source de vérité pour la config** : `vault-config.json` à la racine du vault, lisible par `/vault-setup`, `/daily`, les hooks, et futurs skills.

---

## 2. Approche technique

### Architecture cible du vault

```
mon-vault/
├── CLAUDE.md                         ← instructions perso
├── MEMORY.md                         ← index mémoire
├── vault-config.json                 ← NEW — source de vérité structurée
├── memory/
├── inbox/
├── daily/
├── projects/
├── research/
├── archive/
├── scripts/
│   ├── file_intel.py
│   └── providers/
└── .claude/
    ├── skills/                       ← MIGRÉ depuis skills/ racine
    │   ├── vault-setup/SKILL.md
    │   ├── daily/SKILL.md
    │   ├── tldr/SKILL.md
    │   ├── file-intel/SKILL.md
    │   ├── inbox-zero/SKILL.md
    │   ├── memory-add/SKILL.md
    │   ├── humanise/SKILL.md         ← NEW
    │   └── import-vault/SKILL.md     ← NEW
    ├── hooks/                        ← NEW
    │   ├── session-init.sh
    │   └── skill-discovery.sh
    ├── output-styles/                ← NEW
    │   └── coach.md
    ├── rules/
    │   └── README.md
    └── settings.json                 ← NEW — déclare les hooks
```

### Architecture cible du repo

```
xais-brain/
├── setup.sh                          ← mis à jour (copie depuis .claude/skills/)
├── vault-template/
│   ├── CLAUDE.md
│   ├── MEMORY.md
│   ├── vault-config.json             ← NEW (template, placeholders)
│   ├── memory/README.md
│   └── .claude/
│       ├── skills/                   ← MIGRÉ depuis skills/ repo-racine
│       │   └── [8 skills]
│       ├── hooks/
│       │   ├── session-init.sh
│       │   └── skill-discovery.sh
│       ├── output-styles/
│       │   └── coach.md
│       ├── rules/README.md
│       └── settings.json
├── scripts/
│   ├── file_intel.py
│   └── providers/
└── specs/
```

**Note importante** : on supprime `skills/` à la racine du repo (après copie dans `vault-template/.claude/skills/`). Le setup.sh copie depuis `vault-template/.claude/` vers `$VAULT_PATH/.claude/` d'un coup avec `cp -r`.

### vault-config.json — schéma

```json
{
  "version": "0.2",
  "setupDate": "2026-04-08",
  "user": {
    "name": "Xavier",
    "workMode": "pro+perso"
  },
  "llm": {
    "provider": "gemini",
    "model": null
  },
  "folders": {
    "inbox": "inbox",
    "daily": "daily",
    "projects": "projects",
    "research": "research",
    "archive": "archive",
    "memory": "memory"
  },
  "preferences": {
    "coachMode": false,
    "autoCommit": false
  },
  "adoptedVault": false
}
```

- Lu par `session-init.sh` pour exporter `VAULT_*` env vars.
- Lu par `/vault-setup` pour hydrater les réponses (ou seed si vide).
- Écrit par `/vault-setup` et `/import-vault`.
- `adoptedVault: true` = généré via `/import-vault` (structure user conservée).

### Frontmatter skills enrichi

Format standard à appliquer aux 8 skills :

```yaml
---
name: vault-setup
description: Personnalise le vault Obsidian...
user-invocable: true
disable-model-invocation: false
model: sonnet
---
```

Règles :

- `user-invocable: true` sur les 8 skills FR (ils sont tous déclenchables par slash command).
- `disable-model-invocation: true` sur `humanise` et `import-vault` (actions lourdes, on ne veut pas que Claude les lance automatiquement sur un pattern détecté dans un prompt — l'utilisateur doit explicitement taper `/humanise` ou `/import-vault`).
- `model: sonnet` par défaut. `model: haiku` uniquement pour `daily` et `tldr` (routine rapide, moins de contexte).

### Hook flow

```
SessionStart:
  → session-init.sh
    → lit vault-config.json (si existe)
    → exporte VAULT_PATH, TODAY, YESTERDAY
    → exporte VAULT_INBOX_DIR, VAULT_DAILY_DIR, etc. depuis folders{}
    → si CLAUDE.md absent : echo "tape /vault-setup pour démarrer"
    → si CLAUDE.md présent : echo "Vault: $VAULT_PATH | Aujourd'hui: $TODAY | X fichiers dans inbox"

UserPromptSubmit:
  → skill-discovery.sh
    → lit le prompt sur stdin
    → si match regex \b(skills?|commandes?|que peux-tu|aide|quoi faire)\b
    → liste les skills de $VAULT_PATH/.claude/skills/*/SKILL.md
    → parse frontmatter pour "user-invocable: true"
    → affiche "/nom — description" pour chacun
```

Les deux hooks exit 0 en cas d'erreur (non-bloquants). Messages en FR.

### settings.json du vault

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write(inbox/**)",
      "Write(daily/**)",
      "Write(projects/**)",
      "Write(research/**)",
      "Write(archive/**)",
      "Write(memory/**)",
      "Edit(inbox/**)",
      "Edit(daily/**)",
      "Edit(projects/**)",
      "Edit(research/**)",
      "Edit(memory/**)",
      "Edit(CLAUDE.md)",
      "Edit(MEMORY.md)",
      "Edit(vault-config.json)",
      "Glob",
      "Grep",
      "Bash(ls:*)",
      "Bash(date:*)",
      "Bash(find:*)",
      "Bash(git:*)",
      "Bash(python3:*)",
      "Bash(~/.xais-brain-venv/bin/python3:*)"
    ],
    "deny": [
      "Edit(.claude/**)",
      "Write(.git/**)",
      "Bash(rm -rf:*)"
    ]
  },
  "env": {
    "VAULT_PATH": "${cwd}"
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": ".claude/hooks/session-init.sh" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": ".claude/hooks/skill-discovery.sh", "timeout": 5000 }
        ]
      }
    ]
  }
}
```

Note : `deny Edit(.claude/**)` protège les skills d'écritures accidentelles. `deny Bash(rm -rf:*)` est un filet de sécu.

---

## 3. Phases d'implémentation

### Phase 1 — Migration skills/ → .claude/skills/ + frontmatter enrichi

**Objectif** : déplacer les 6 skills existants dans la bonne structure et enrichir leur frontmatter.

1. Créer `vault-template/.claude/skills/` (dossier cible).
2. Déplacer chaque skill depuis `skills/<name>/SKILL.md` → `vault-template/.claude/skills/<name>/SKILL.md` (via `git mv` pour préserver l'historique).
3. Pour chaque skill, enrichir le frontmatter YAML :
   - Ajouter `user-invocable: true`.
   - Ajouter `disable-model-invocation: false`.
   - Ajouter `model: sonnet` (ou `haiku` pour `daily` et `tldr`).
4. Supprimer le dossier `skills/` à la racine du repo (devenu vide).
5. Mettre à jour `setup.sh` — `step6_skills()` :
   - Lire depuis `$SCRIPT_DIR/vault-template/.claude/skills/` au lieu de `$SCRIPT_DIR/skills/`.
   - Copier dans `$VAULT_PATH/.claude/skills/` ET `$HOME/.claude/skills/` (inchangé pour le global).
   - Ajouter une logique de migration : si l'utilisateur a un ancien vault avec `$VAULT_PATH/skills/<name>/SKILL.md` (sans `.claude/`), logguer un warning et laisser l'ancienne struct (l'user décidera de nettoyer).

**Test manuel** :

```bash
bash setup.sh
# vérifier : ls ~/xais-brain-vault/.claude/skills/ doit montrer 6 skills
# vérifier : ls ~/.claude/skills/ doit contenir vault-setup daily etc.
# vérifier : head -10 d'un SKILL.md doit montrer le frontmatter enrichi
```

### Phase 2 — vault-config.json (template + écriture par setup.sh)

**Objectif** : créer la source de vérité structurée et la populer au setup.

1. Créer `vault-template/vault-config.json` avec les placeholders :

```json
{
  "version": "0.2",
  "setupDate": null,
  "user": { "name": null, "workMode": null },
  "llm": { "provider": "gemini", "model": null },
  "folders": {
    "inbox": "inbox", "daily": "daily", "projects": "projects",
    "research": "research", "archive": "archive", "memory": "memory"
  },
  "preferences": { "coachMode": false, "autoCommit": false },
  "adoptedVault": false
}
```

2. Dans `setup.sh`, `step7_llm_config()` : après avoir déterminé `$llm_name`, écrire ou mettre à jour `vault-config.json` via un petit snippet Python inline :

```bash
python3 - "$VAULT_PATH" "$llm_name" <<'PYEOF'
import json, sys, os
from datetime import date
vault, provider = sys.argv[1], sys.argv[2]
cfg_path = os.path.join(vault, "vault-config.json")
try:
    with open(cfg_path) as f: cfg = json.load(f)
except FileNotFoundError:
    cfg = {"version": "0.2", "folders": {"inbox":"inbox","daily":"daily","projects":"projects","research":"research","archive":"archive","memory":"memory"}, "preferences": {"coachMode": False, "autoCommit": False}, "adoptedVault": False}
cfg.setdefault("user", {"name": None, "workMode": None})
cfg["llm"] = {"provider": provider, "model": None}
cfg["setupDate"] = cfg.get("setupDate") or date.today().isoformat()
with open(cfg_path, "w") as f: json.dump(cfg, f, indent=2)
PYEOF
```

3. Mettre à jour `vault-template/CLAUDE.md` pour mentionner `vault-config.json` comme source de vérité (1-2 lignes, pas plus).

**Test manuel** : après setup, `cat ~/xais-brain-vault/vault-config.json` doit renvoyer un JSON valide avec provider rempli et setupDate = today.

### Phase 3 — Hooks session-init.sh + skill-discovery.sh (FR)

**Objectif** : créer les deux hooks shell en français, portés depuis `obsidian-claude-pkm`.

1. Créer `vault-template/.claude/hooks/session-init.sh` :

```bash
#!/bin/bash
# Hook SessionStart — charge le contexte vault au démarrage de Claude Code
# Non-bloquant : exit 0 en cas d'erreur

export VAULT_PATH="${VAULT_PATH:-$(pwd)}"
export TODAY=$(date +%Y-%m-%d)
export YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

# Lecture de vault-config.json si présent
CFG="$VAULT_PATH/vault-config.json"
if [ -f "$CFG" ]; then
    # Parse minimal via python stdlib (pas de dep jq)
    eval "$(python3 -c "
import json,sys
try:
    cfg = json.load(open('$CFG'))
    f = cfg.get('folders', {})
    for k, v in f.items():
        print(f'export VAULT_{k.upper()}_DIR=\"{v}\"')
except Exception: pass
" 2>/dev/null)"
fi

# Défauts si vault-config absent
: "${VAULT_INBOX_DIR:=inbox}"
: "${VAULT_DAILY_DIR:=daily}"
: "${VAULT_PROJECTS_DIR:=projects}"

# Pas de CLAUDE.md → vault non configuré
if [ ! -f "$VAULT_PATH/CLAUDE.md" ]; then
    echo ""
    echo "Ce dossier ne ressemble pas à un vault xais-brain."
    echo "  → Lance : curl -fsSL https://raw.githubusercontent.com/XAISOLUCES/xais-brain/main/setup.sh | bash"
    exit 0
fi

# Surface minimal — 3 lignes max
INBOX_COUNT=$(find "$VAULT_PATH/$VAULT_INBOX_DIR" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "Vault  : $(basename "$VAULT_PATH")  |  Aujourd'hui : $TODAY"
if [ "$INBOX_COUNT" -gt 0 ]; then
    echo "Inbox  : $INBOX_COUNT fichiers en attente  → /inbox-zero"
fi
DAILY_TODAY="$VAULT_PATH/$VAULT_DAILY_DIR/$TODAY.md"
if [ ! -f "$DAILY_TODAY" ]; then
    echo "Note du jour absente  → /daily"
fi
exit 0
```

2. Créer `vault-template/.claude/hooks/skill-discovery.sh` (FR, porté depuis le repo réf) :

```bash
#!/bin/bash
# Hook UserPromptSubmit — liste les skills dispos quand l'user le demande
# Non-bloquant : exit 0 toujours

PROMPT=$(cat)

# Déclencheurs FR + EN minimal
if echo "$PROMPT" | grep -iqE '\b(skills?|commandes?|que peux[- ]tu|aide[ -]moi|quoi faire|slash)\b'; then
    echo ""
    echo "Skills disponibles (tape /nom pour lancer) :"
    echo ""
    SKILLS_DIR="$(pwd)/.claude/skills"
    if [ -d "$SKILLS_DIR" ]; then
        for dir in "$SKILLS_DIR"/*/; do
            [ -f "$dir/SKILL.md" ] || continue
            name=$(basename "$dir")
            desc=$(sed -n '/^---$/,/^---$/{/^description:/{s/^description: *//;p;q;}}' "$dir/SKILL.md")
            invocable=$(sed -n '/^---$/,/^---$/{/^user-invocable:/{s/^user-invocable: *//;p;q;}}' "$dir/SKILL.md")
            if [ "$invocable" = "true" ]; then
                printf "  /%-15s — %s\n" "$name" "$desc"
            fi
        done
    fi
    echo ""
fi
exit 0
```

3. `chmod +x` les deux dans le vault-template (sera préservé par `cp -a` ou `cp` + chmod dans setup.sh).
4. Mettre à jour `setup.sh` : `step6_skills()` doit aussi copier `.claude/hooks/` et `chmod +x` les scripts.

**Test manuel** :

```bash
cd ~/xais-brain-vault && claude
# Au démarrage : message "Vault : xais-brain-vault | Aujourd'hui : 2026-04-08 | Inbox : 0 fichiers"
# Taper : "quelles sont les commandes dispo ?"
# Doit lister les 8 skills
```

### Phase 4 — Skill /humanise (dé-IA-ification FR)

**Objectif** : porter `de-ai-ify` en français, adapté au style de voix FR.

1. Créer `vault-template/.claude/skills/humanise/SKILL.md` :

```markdown
---
name: humanise
description: Nettoyer un texte AI-ifié pour restaurer une voix naturelle française. Enlève les tics IA (« moreover », « il est important de noter », « exploitons »), les transitions mécaniques, et les listes à rallonge. Utiliser pour humanise, dé-IA-ifier, nettoyer ce texte, rendre plus humain.
user-invocable: true
disable-model-invocation: true
model: sonnet
---

# humanise

Restaure une voix humaine dans un texte marqué IA. Produit un fichier `<nom>-humanise.md` et un changelog des modifs.

## Entrée

Chemin d'un fichier `.md` ou `.txt`. Si l'utilisateur ne précise pas, demander.

## Ce qu'on enlève

### 1. Transitions mécaniques
- « De plus », « Par ailleurs », « En outre », « Néanmoins », « Toutefois » (en excès)
- Ouvertures « Bien que X, Y »
- « Il convient de noter que »

### 2. Clichés IA
- « Dans un monde en constante évolution »
- « Plongeons au cœur de »
- « Libérer ton potentiel »
- « Exploiter la puissance de »
- « C'est crucial de comprendre »

### 3. Verbes corporate
- `utiliser` (en excès) → `prendre`, `se servir de`
- `optimiser` → `améliorer`
- `faciliter` → `aider`
- `exploiter` → `utiliser`
- `tirer parti de` → `utiliser`
- `implémenter` → `mettre en place`

### 4. Quantificateurs vagues
- « divers », « plusieurs », « de multiples », « une myriade »
- « relativement », « généralement » (quand l'auteur connaît la réponse)

### 5. Motifs robotiques
- Questions rhétoriques suivies de leurs réponses immédiates
- Parallélismes obsessionnels (toujours exactement 3 exemples)
- Annonces d'emphase (« Il est crucial de comprendre que... »)
- Conclusions qui paraphrasent l'intro

## Ce qu'on garde ou ajoute

- Phrases de longueurs variées
- Ton direct, affirmatif
- Exemples concrets à la place de généralités
- Rythme naturel (pas de structure « 3 bullets + conclusion »)
- Le « je » si l'original l'utilisait

## Process

1. Lire le fichier source.
2. Appliquer les transformations (pattern par pattern).
3. Écrire le résultat dans `<nom>-humanise.md` dans le même dossier.
4. Logger un changelog : combien de tics enlevés, combien de phrases reformulées, et marquer les passages qui gagneraient un exemple concret (à compléter par l'user).

## Exemple

**Avant (IA)** :
> Dans l'écosystème numérique actuel en constante évolution, il est crucial de comprendre que tirer parti de l'intelligence artificielle de manière efficace n'est pas simplement une question d'utiliser des technologies de pointe — c'est exploiter son potentiel transformateur pour libérer des opportunités sans précédent.

**Après (humain)** :
> L'IA marche mieux quand tu l'utilises pour des tâches précises. Écris du code, analyse des données, réponds à des questions. Le reste est du marketing.

## Sortie finale

- Fichier `<nom>-humanise.md` créé
- Changelog affiché dans le chat : « 12 tics IA enlevés, 4 phrases reformulées, 2 passages à enrichir d'un exemple concret »
```

**Test manuel** :

Créer un `test.md` avec un paragraphe IA-ifié, lancer `/humanise test.md`, vérifier que `test-humanise.md` apparaît avec un changelog sensé.

### Phase 5 — Skill /import-vault (adopt light FR)

**Objectif** : permettre à un utilisateur avec un vault Obsidian existant d'adopter le système xais-brain sans casser sa structure.

**Différences volontaires par rapport à `/adopt` de la ref** :

- Pas de cascade de goals à scaffolder (xais-brain n'a pas de cascade).
- Pas de détection de « méthode » (PARA / Zettelkasten / Johnny Decimal) — trop d'overhead.
- Mapping simplifié : on demande 5 dossiers (inbox, daily, projects, research, archive) et c'est tout.

1. Créer `vault-template/.claude/skills/import-vault/SKILL.md` :

```markdown
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
```

**Test manuel** :

```bash
# Dans un vault Obsidian existant fictif
mkdir -p /tmp/fake-vault/{00_Inbox,Daily,01_Projects,.obsidian}
touch /tmp/fake-vault/Daily/2026-04-07.md
cd /tmp/fake-vault && claude
# /import-vault
# Répondre aux questions → vérifier que vault-config.json, CLAUDE.md, memory/ sont créés
```

### Phase 6 — Output style coach.md (FR)

**Objectif** : offrir un mode « coach » FR activable via `/output-style coach` pour les utilisateurs qui veulent un ton plus challengeant.

1. Créer `vault-template/.claude/output-styles/coach.md` — traduction/adaptation FR du coach.md de la ref :

```markdown
---
name: Coach FR
description: Accompagnement focalisé sur l'action et l'accountability — challenge les hypothèses, confronte aux objectifs, pousse à agir plutôt qu'à planifier.
---

Tu es un coach de productivité. Ton rôle : aider l'utilisateur à rester accountable sur ses engagements et à passer à l'action plutôt qu'à sur-planifier.

## Principes

**Clarifier l'intention** : si l'objectif est flou, pose 1-2 questions de clarification avant de donner un conseil. Pas plus.
- « À quoi ressemblerait un vrai succès ici ? »
- « Comment ça s'aligne avec ton objectif principal ? »

**Challenge avec respect** : note les écarts entre ce que l'utilisateur dit vouloir et ce qu'il fait.
- « Tu m'as dit que X était prioritaire, mais tu passes du temps sur Y. Qu'est-ce qui se passe ? »

**Tenir accountable** : référence les engagements passés de l'utilisateur (notes, projets, daily).
- « Tu t'étais engagé à finir ça vendredi. Où ça en est ? »

**Révéler les patterns** : surface les thèmes récurrents.
- « Je remarque que tu planifies ambitieux mais reportes systématiquement le travail le plus important. Qu'est-ce qu'il y a derrière cette résistance ? »

## Style de communication

**Questions puissantes** (préférer aux affirmations) :
- « Qu'est-ce qui se passerait si tu shippais aujourd'hui au lieu de peaufiner demain ? »
- « Comment tu aborderais ça si tu n'avais qu'une semaine pour y arriver ? »
- « Quelle est la plus petite action que tu peux faire maintenant pour créer du momentum ? »
- « Que ferait la version future de toi qui a déjà atteint cet objectif ? »

**Mots-clés à bannir** :
- Pas de « exploite », « libère ton potentiel », « en constante évolution »
- Pas de « il est crucial de », « il convient de noter »
- Pas de listes à rallonge — au max 3 bullets, de préférence 1 action.

**Langage de l'utilisateur** : reprends ses termes, ses projets, ses mots. Pas de jargon importé.

## Focus exécution

**La SEULE chose** : quand l'utilisateur est éparpillé, demande :
- « Quelle est LA chose qui rendrait tout le reste plus facile ou inutile ? »

**Done > Perfect** : quand le perfectionnisme bloque :
- « C'est quoi la version minimale que tu peux finir aujourd'hui ? »

**Action > Planification** : quand il sur-planifie :
- « T'as assez réfléchi. Quelle action concrète tu peux faire dans l'heure qui vient ? »

**La résistance comme signal** : quand il bloque :
- « C'est quoi qui te résiste le plus ? C'est souvent là qu'il y a le plus d'enjeu. »

## Structure de réponse

1. **Valider** ce qu'il a partagé ou accompli.
2. **Observer** un pattern ou un décalage sans juger.
3. **Questionner** pour creuser ou challenger.
4. **Proposer** une action ou un reframing.
5. **Engager** : demander un next step concret.

Termine chaque interaction par :
- Une action spécifique, faisable **immédiatement** (pas « demain », pas « cette semaine »).
- Une question qui crée de l'accountability (« Tu me dis quoi quand c'est fait ? »).

**Interdit** :
- Pas de félicitations creuses (« super initiative ! »).
- Pas de résumés exhaustifs.
- Pas de validation automatique — si l'user dit qu'il va faire X et que X est flou, demande une version plus concrète avant d'accepter.
```

**Test manuel** :

```bash
cd ~/xais-brain-vault && claude
# /output-style
# Sélectionner « Coach FR »
# Envoyer un message vague type « je sais pas trop sur quoi bosser »
# Vérifier que la réponse challenge + propose 1 action + pose 1 question d'engagement
```

### Phase 7 — Update setup.sh, CLAUDE.md, README, .env.example

**Objectif** : s'assurer que tout le nouveau est installable via le one-liner et documenté.

1. **`setup.sh`** :
   - `step5_vault()` : ajouter la copie de `vault-template/vault-config.json` si absent.
   - `step6_skills()` : copier depuis `vault-template/.claude/skills/` au lieu de `skills/`. Copier aussi `.claude/hooks/`, `.claude/output-styles/`, `.claude/settings.json` d'un coup via `cp -R vault-template/.claude/* "$VAULT_PATH/.claude/"`. Chmod +x les hooks.
   - `step7_llm_config()` : écrire le provider dans `vault-config.json` (Phase 2).
   - `verify_install()` : ajouter un check de `vault-config.json` et des 2 hooks.
   - `print_done()` : mentionner `/import-vault` et `/humanise` dans la liste des skills.
   - Compter : `NUM_STEPS` reste à 9 (on n'ajoute pas d'étape).
   - **Migration ancien vault** : dans `step5_vault`, si `$VAULT_PATH/skills/` existe (ancien layout) et `$VAULT_PATH/.claude/skills/` n'existe pas, logguer un warning et suggérer de supprimer l'ancien manuellement.

2. **`vault-template/CLAUDE.md`** :
   - Ajouter une mention 1-ligne de `vault-config.json` dans la section « Structure du vault ».
   - Ajouter `/humanise` et `/import-vault` dans la liste des slash commands.

3. **`README.md`** :
   - Mettre à jour le tableau des skills (6 → 8).
   - Mentionner le nouveau flow : « déjà un vault ? → `/import-vault` ».
   - Remplacer toute occurrence de `skills/` (racine) par `.claude/skills/` dans la doc d'install manuelle.
   - Ajouter une ligne sur `vault-config.json` dans « Structure du vault ».
   - Ajouter une mention de l'output style coach dans une section « Personnalisation ».

4. **`.env.example`** : inchangé (la config est dans `vault-config.json`, mais les clés API restent dans `.env` pour sécu).

### Phase 8 — Validation et tests manuels

**Objectif** : valider que l'ensemble fonctionne sans régression.

**Checklist** :

1. `bash setup.sh` sur un dossier vide :
   - [ ] Crée `$VAULT_PATH/.claude/skills/` avec 8 skills.
   - [ ] Crée `$VAULT_PATH/.claude/hooks/` avec 2 scripts exécutables.
   - [ ] Crée `$VAULT_PATH/.claude/output-styles/coach.md`.
   - [ ] Crée `$VAULT_PATH/.claude/settings.json`.
   - [ ] Crée `$VAULT_PATH/vault-config.json` avec `llm.provider` rempli.
   - [ ] Les skills globaux `~/.claude/skills/` contiennent les 8 skills.

2. `bash setup.sh` sur un vault existant xais-brain (ancien layout `skills/`) :
   - [ ] Warning affiché : « ancien layout détecté, le nouveau layout est dans .claude/skills/ ».
   - [ ] Ne casse rien.
   - [ ] Le nouveau `.claude/skills/` est créé à côté.

3. `cd $VAULT_PATH && claude` :
   - [ ] Hook session-init affiche les 3 lignes FR.
   - [ ] Taper « c'est quoi les commandes ? » → le hook skill-discovery liste les 8 skills.
   - [ ] `/daily` marche comme avant (régression).
   - [ ] `/vault-setup` marche comme avant et met à jour `vault-config.json`.
   - [ ] `/humanise test.md` crée `test-humanise.md`.
   - [ ] `/import-vault` dans un vault non-xais-brain fonctionne.
   - [ ] `/output-style` propose « Coach FR ».

4. `bash setup.sh` une deuxième fois sur le même vault (idempotence) :
   - [ ] Rien ne casse.
   - [ ] `vault-config.json` n'est pas réécrit avec des valeurs nulles (preserve l'existant).
   - [ ] Les skills ne sont pas dupliqués.

---

## 4. Ordre d'exécution recommandé

Les phases sont ordonnées pour que chaque phase puisse être validée avant de passer à la suivante. Build et test en séquence :

```
Phase 1  →  Migration + frontmatter  (test: les 6 skills existants marchent toujours)
Phase 2  →  vault-config.json         (test: JSON valide écrit au setup)
Phase 3  →  Hooks FR                  (test: messages s'affichent au démarrage)
Phase 4  →  /humanise                 (test: dé-IA-ifie un paragraphe)
Phase 5  →  /import-vault             (test: adopte un vault Obsidian factice)
Phase 6  →  Coach FR                  (test: output-style activable)
Phase 7  →  setup.sh + docs           (test: curl|bash complet fonctionne)
Phase 8  →  Validation end-to-end     (checklist complète)
```

---

## 5. Cas limites et gestion d'erreurs

### Hooks

- **Python absent** : les hooks utilisent `python3` pour parser `vault-config.json`. Si absent, fallback silencieux sur les défauts (`inbox`, `daily`, etc.).
- **vault-config.json corrompu** : `try/except` dans le snippet Python, fallback sur les défauts.
- **PATH sans `python3`** : le hook logue rien et utilise les défauts.
- **Permissions bash** : les hooks doivent être `chmod +x`. Le setup.sh le fait explicitement.

### vault-config.json

- **Écrasement** : `setup.sh` ne doit **jamais** écraser un `vault-config.json` existant en entier. Il merge : lit l'ancien, update `llm.provider` et `setupDate` seulement si absent, réécrit.
- **Version bump futur** : le champ `version` permettra plus tard de faire des migrations si le schéma change.

### Migration ancien layout

- Si un utilisateur a un vault xais-brain d'une version précédente avec `$VAULT_PATH/skills/`, on ne supprime rien automatiquement. Warning + `.claude/skills/` en parallèle. L'user nettoie à la main quand il est prêt.

### /import-vault

- **Vault vide** (pas de `.md`) : warning, suggère `/vault-setup` à la place.
- **Déjà adopté** : propose de regénérer (réécrit vault-config.json, pas CLAUDE.md sans backup).
- **CLAUDE.md existant** : backup puis remplace. Pas de merge auto (trop fragile) — l'user mergera à la main via le backup référencé.

### /humanise

- **Fichier introuvable** : demande un path valide.
- **Fichier vide** : warning, pas d'écriture.
- **Fichier déjà humanisé** (`-humanise.md` existe) : demande écrasement.

---

## 6. Critères de succès

Le build est réussi si :

1. **Zero régression** : les 6 skills existants marchent toujours identiquement.
2. **One-liner toujours vert** : `curl -fsSL ...setup.sh | bash` installe tout sans erreur sur un dossier vide.
3. **Idempotence préservée** : relancer `setup.sh` ne casse aucun vault existant.
4. **`/import-vault`** peut adopter un vault Obsidian factice en 3 minutes.
5. **`/humanise`** nettoie un paragraphe IA-ifié en FR avec un changelog.
6. **Hooks** s'exécutent au démarrage et affichent du FR (3 lignes max pour session-init).
7. **`vault-config.json`** est écrit, valide, et lu par les hooks.
8. **Coach FR** activable via `/output-style coach`.
9. **Frontmatter enrichi** sur les 8 skills (vérifiable via `grep user-invocable .claude/skills/*/SKILL.md`).
10. **README à jour** : 8 skills listés, mention `/import-vault`, mention `vault-config.json`.

---

## 7. Estimation

- **Phase 1** (migration + frontmatter) : 30 min — mostly renommage + YAML.
- **Phase 2** (vault-config.json) : 45 min — schema + snippet Python + tests.
- **Phase 3** (hooks FR) : 1h — 2 scripts bash + tests.
- **Phase 4** (/humanise) : 45 min — SKILL.md + test sur un fichier réel.
- **Phase 5** (/import-vault) : 1h30 — le plus gros, beaucoup de logique interactive.
- **Phase 6** (coach FR) : 30 min — traduction + test.
- **Phase 7** (setup.sh + docs) : 1h — update + tests d'install.
- **Phase 8** (validation) : 45 min — checklist complète.

**Total** : ~6h30 de build focused.

---

## 8. Références

- `/tmp/obsidian-claude-pkm/vault-template/.claude/` — source des hooks, adopt, coach.md.
- `/tmp/claudesidian/.claude/commands/de-ai-ify.md` — source de /humanise.
- `/tmp/obsidian-claude-pkm/vault-template/.claude/settings.json` — schéma permissions.
- `/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/setup.sh` — script à mettre à jour.
- `/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/vault-template/CLAUDE.md` — template à enrichir.

---

**Prochaine étape** : lancer `/XD-build specs/todo/enrich-xais-brain-pkm-best-of.md` pour implémenter.
