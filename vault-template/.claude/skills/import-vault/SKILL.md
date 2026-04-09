---
name: import-vault
description: Adopte un vault Obsidian existant dans xais-brain sans casser sa structure. Scanne les dossiers, détecte les rôles avec fallback par nom, propose un mapping interactif, écrit vault-config.json, backup + merge CLAUDE.md, installe les skills et hooks manquants en mode additif strict. Préserve tous les skills et dossiers custom de l'utilisateur. Utiliser quand l'utilisateur dit import-vault, adopter mon vault, BYOV, j'ai déjà un vault Obsidian.
user-invocable: true
disable-model-invocation: true
model: sonnet
allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion
---

<objective>
Bring Your Own Vault — installer xais-brain sur un vault Obsidian existant sans toucher à la structure. Le skill est **non-destructif** et **idempotent** : aucun fichier utilisateur n'est supprimé ou écrasé sans backup horodaté, aucun skill custom n'est touché, aucun dossier n'est vidé.

À utiliser quand l'utilisateur a déjà un vault Obsidian structuré (PARA, Zettelkasten, layout custom) et veut bénéficier des skills et hooks xais-brain sans repartir de zéro.
</objective>

<prerequisites>
- L'utilisateur lance `claude` depuis la racine du vault cible.
- Un dossier `.obsidian/` est présent à la racine (sinon demander confirmation pour continuer).
- xais-brain est accessible via `$XAIS_BRAIN_REPO` ou le fallback `~/Dev/XAIS_2ND_BRAIN/xais-brain/vault-template/` pour la copie des skills et hooks.
- **Recommandation forte** : l'utilisateur fait `cp -r vault vault.backup-pre-import` avant de lancer — le skill ne propose pas de rollback automatique.
</prerequisites>

<quick_start>
Depuis la racine du vault cible :

```bash
cd ~/mon-vault-existant
cp -r . ../vault.backup-pre-import   # filet de sécurité recommandé
claude
```

Puis : `/import-vault`. Le skill enchaîne 4 phases séquentielles (scan → mapping interactif → écriture additive → validation). La première interaction utilisateur arrive au début de la phase 2.
</quick_start>

<workflow>
Le processus comporte 4 phases séquentielles :

1. **Scan** — détection des dossiers top-level, signaux de contenu, fallback par nom, skills custom existants
2. **Mapping** — 2 rounds `AskUserQuestion` (4 items max par round) pour les 5 mappings + 3 préférences
3. **Écriture additive** — `vault-config.json`, `memory/`, backup + nouveau `CLAUDE.md`, `.claude/hooks/`, `.claude/output-styles/`, `.claude/settings.json`, skills xais-brain manquants
4. **Validation** — JSON valide, dossiers mappés existent, skills custom préservés, résumé utilisateur
</workflow>

<phase_1_scan>
Scanner le vault depuis sa racine. **Critique** : prévoir un fallback par nom car les vaults squelettes (dossiers vides) ne génèrent aucun signal de contenu.

**Étape A — Lister les top-level dirs**, en excluant `.obsidian`, `.git`, `.claude`, `.trash`, `node_modules`, `.DS_Store` :

```bash
find . -mindepth 1 -maxdepth 1 -type d \
  ! -name '.obsidian' ! -name '.git' ! -name '.claude' \
  ! -name '.trash' ! -name 'node_modules' | sort
```

**Étape B — Pour chaque dossier, compter les `.md` et détecter les signaux de contenu** :

- Nombre total de `.md` (récursif, maxdepth 5)
- Fichiers au format `YYYY-MM-DD*.md` → signal `daily`
- Sous-dossiers contenant `CLAUDE.md` ou `README.md` → signal `projects`
- Nom du dossier matchant (case-insensitive) :
  - `inbox`, `boîte`, `à trier`, `triage` → signal `inbox`
  - `daily`, `journal`, `diary`, `jour` → signal `daily`
  - `project`, `projet` → signal `projects`
  - `research`, `recherche`, `knowledge`, `notes`, `zettelkasten`, `zk` → signal `research`
  - `archive`, `archiv` → signal `archive`

**Étape C — Fallback par nom pur** : si aucun signal n'est détecté pour un rôle (cas vault squelette ou vault vide), proposer comme candidat n'importe quel dossier dont le nom matche **exactement** (case-insensitive) l'un des 5 rôles canoniques (`inbox`, `daily`, `projects`, `research`, `archive`). C'est un candidat de **niveau 2** — plus faible qu'un signal de contenu mais meilleur qu'aucun candidat.

**Étape D — Détecter `memory.md` racine** : `test -f memory.md` (fichier, pas dossier `memory/`). Si présent, c'est un **cas ambigu** — le skill ne touche jamais à ce fichier mais propose une migration manuelle dans le nouveau `CLAUDE.md`.

**Étape E — Scanner `.claude/skills/` existant** : lister tous les skills présents. Classifier en 3 catégories :

- **Canoniques xais-brain** (à ne pas toucher, déjà présents) : `daily, file-intel, humanise, import-vault, inbox-zero, memory-add, tldr, vault-setup`
- **Kepano optionnels** (à préserver) : `defuddle, json-canvas, obsidian-bases, obsidian-cli, obsidian-markdown`
- **Custom utilisateur** (à préserver **absolument** et lister dans le nouveau `CLAUDE.md`) : tout autre nom

**Étape F — Lister les dossiers non-canoniques** : tout dossier top-level qui n'est pas un candidat pour l'un des 5 rôles. Ces dossiers iront dans `vault-config.json.customFolders` pour documentation, sans être touchés.

**Étape G — Afficher le résumé du scan** :

```
Scan du vault terminé.

342 notes dans 6 dossiers :
  00_Inbox/       → 15 notes     (signal: nom "inbox")          → candidat inbox
  01_Projects/    → 45 notes     (signal: sous-dossiers README) → candidat projects
  02_Areas/       → 23 notes                                    → customFolder
  03_Resources/   → 87 notes     (signal: nom "research")       → candidat research
  04_Archive/     → 67 notes     (signal: nom "archive")        → candidat archive
  Daily/          → 180 notes    (signal: 180 dates YYYY-MM-DD) → candidat daily

Détecté :
  memory.md (fichier racine) — cas ambigu, migration proposée en phase 3
  .claude/skills/ : 3 skills custom (client, project, workflow) → à préserver

Aucun rôle orphelin.
```
</phase_1_scan>

<phase_2_mapping>
**Contrainte technique** : `AskUserQuestion` accepte **4 questions maximum par appel**. Le mapping complet (5 rôles + 3 préférences = 8 questions) doit donc être réparti sur **2 rounds**.

**Round 1 — 4 premiers rôles** :

1. Quel dossier joue le rôle `inbox` ? (candidats du scan + "Utiliser standard inbox/" + "Skip")
2. Quel dossier joue le rôle `daily` ? (candidats + standard + skip)
3. Quel dossier joue le rôle `projects` ? (candidats + standard + skip)
4. Quel dossier joue le rôle `research` ? (candidats + standard + skip)

**Round 2 — Archive + 3 préférences** :

1. Quel dossier joue le rôle `archive` ? (candidats + standard + skip)
2. Nom du vault (3 options + "Other" pour texte libre)
3. Work mode : `mixed` (pro + perso) / `pro` / `perso`
4. Activer le mode coach FR dès l'adoption : oui / non

**Règles de mapping** :

- L'option "Utiliser standard X/" (ou "Créer nouveau X/") est **idempotente** : si le dossier existe déjà, le réutiliser tel quel sans recréation ni vidage. Jamais destructive. Si absent, `mkdir -p`.
- L'option "Skip" omet le rôle de `vault-config.json.folders` (le rôle n'existe simplement pas dans ce vault).
- Le rôle `memory` n'est **pas** dans le mapping : convention xais-brain systématique, créée en phase 3 sauf si `memory/` existe déjà.
- Les 4 questions de personnalisation profonde (rôle utilisateur, priorités, style) sont **déléguées à `/vault-setup`** après l'adoption. `/import-vault` se limite au mapping structurel et aux préférences essentielles.
</phase_2_mapping>

<phase_3_writes>
Écriture **strictement additive**. Règle absolue : jamais écraser un fichier utilisateur existant sans backup horodaté.

**3.1 — `vault-config.json`** (racine du vault)

Si absent, écrire le schéma suivant (remplacer les placeholders) :

```json
{
  "version": "0.2",
  "name": "<nom choisi>",
  "setupDate": "<YYYY-MM-DD>",
  "adoptedVault": true,
  "user": { "name": null, "workMode": "<mixed|pro|perso>" },
  "llm": { "provider": null, "model": null },
  "folders": {
    "inbox": "<mapping>",
    "daily": "<mapping>",
    "projects": "<mapping>",
    "research": "<mapping>",
    "archive": "<mapping>",
    "memory": "memory"
  },
  "preferences": { "coachMode": <bool>, "autoCommit": false },
  "customFolders": ["<dossiers non-canoniques>"],
  "customSkills": ["<skills user préservés>"]
}
```

Si présent **et** `adoptedVault: true` → demander "Régénérer la config ?" avant tout writing. Sinon abort avec un message clair.

Les rôles "skip" sont omis de `folders` (pas inscrits avec valeur vide).

**3.2 — `memory/` et `memory/README.md`**

```bash
mkdir -p memory
```

Écrire `memory/README.md` uniquement s'il n'existe pas. **Ne jamais** écraser un `memory/README.md` existant.

**3.3 — `memory.md` racine** (cas ambigu)

Si un fichier `memory.md` existe à la racine, **ne jamais le toucher**. Inclure une note dans le nouveau `CLAUDE.md` :

```
> Note : un fichier `memory.md` existe à la racine (non migré par l'adoption). Pour
> l'intégrer dans la convention xais-brain : `mv memory.md memory/session-log.md`.
```

**3.4 — Backup et nouveau `CLAUDE.md`**

Si `CLAUDE.md` existe :

```bash
TS=$(date +%Y-%m-%d-%H%M%S)
cp CLAUDE.md "CLAUDE.md.backup-$TS"
```

Écrire un nouveau `CLAUDE.md` qui contient :

- Header mentionnant la date d'adoption et le nom du backup
- Section structure du vault avec le **mapping réel** (pas le template générique) — documenter explicitement chaque alias non-standard (ex : `projects → clients/`)
- Les `customFolders` listés avec un commentaire "conservés hors mapping xais-brain"
- La note `memory.md` si applicable (voir 3.3)
- Section "Slash commands disponibles" listant :
  - Les 8 skills xais-brain core
  - Une sous-section "Custom (préservés)" avec les skills custom détectés en phase 1
- Section "Historique" avec une référence **en prose** au backup :

```markdown
## Historique

Le `CLAUDE.md` original pré-adoption est conservé dans `CLAUDE.md.backup-<TS>`.
Consulter ce fichier pour retrouver le contexte d'origine ; les conventions
importantes peuvent être migrées à la main dans ce fichier ou dans
`.claude/rules/`.
```

Ne **pas** utiliser `@import` — ce n'est pas une directive native Claude Code, juste une convention xais-brain optionnelle qui n'est pas interprétée automatiquement à la lecture du CLAUDE.md.

**3.5 — Structure `.claude/`**

```bash
mkdir -p .claude/hooks .claude/output-styles .claude/rules .claude/skills
```

Copier depuis `${XAIS_BRAIN_REPO:-$HOME/Dev/XAIS_2ND_BRAIN/xais-brain}/vault-template/.claude/` :

- `hooks/session-init.sh`, `hooks/skill-discovery.sh` → `chmod +x` après copie
- `output-styles/coach.md`
- `settings.json`

**Règle no-clobber** : utiliser `cp -n` (ou tester `[ -f target ]` avant) pour chaque fichier. Jamais écraser un fichier existant de l'utilisateur. Si `.claude/settings.json` existe déjà, afficher un warning et laisser l'utilisateur gérer le merge manuel.

**3.6 — Skills xais-brain (mode additif strict)**

Liste canonique : `daily, file-intel, humanise, import-vault, inbox-zero, memory-add, tldr, vault-setup`.

Pour chaque skill canonique :

```bash
if [ ! -d ".claude/skills/$skill" ]; then
  mkdir -p ".claude/skills/$skill"
  cp "$SRC/.claude/skills/$skill/SKILL.md" ".claude/skills/$skill/"
fi
```

**Ne jamais** écraser un skill existant, même s'il s'agit d'un skill canonique xais-brain. Si l'utilisateur a une version custom de `daily/` (par exemple), elle est respectée — il migrera manuellement s'il le souhaite. Les skills Kepano optionnels et les skills custom sont laissés strictement intacts.
</phase_3_writes>

<phase_4_validation>
Vérifier l'intégrité de l'adoption avant d'afficher le résumé final.

```bash
# JSON valide
python3 -m json.tool vault-config.json >/dev/null && echo "OK vault-config.json"
python3 -m json.tool .claude/settings.json >/dev/null && echo "OK settings.json"

# Dossiers mappés existent effectivement
python3 -c "
import json
cfg = json.load(open('vault-config.json'))
for role, path in cfg['folders'].items():
    import os
    status = 'OK' if os.path.isdir(path) else 'MISSING'
    print(f'{status}  {role} → {path}')
"

# Hooks exécutables
[ -x .claude/hooks/session-init.sh ] && echo "OK session-init +x"
[ -x .claude/hooks/skill-discovery.sh ] && echo "OK skill-discovery +x"

# Backup CLAUDE.md présent (si existait)
ls CLAUDE.md.backup-* 2>/dev/null && echo "OK backup" || echo "no prior CLAUDE.md to backup"

# Skills custom préservés
python3 -c "
import json, os
cfg = json.load(open('vault-config.json'))
for s in cfg.get('customSkills', []):
    status = 'OK' if os.path.isdir(f'.claude/skills/{s}') else 'LOST'
    print(f'{status}  custom skill: {s}')
"
```

Afficher le résumé final :

```
Vault adopté sans toucher à ta structure.

Mapping :
  inbox    → 00_Inbox/
  daily    → Daily/
  projects → 01_Projects/
  research → 03_Resources/
  archive  → 04_Archive/
  memory   → memory/ (créé)

Préservé :
  CLAUDE.md original → CLAUDE.md.backup-<TS>
  3 skills custom intacts : client, project, workflow
  memory.md (racine, non migré — voir note dans CLAUDE.md)
  3 customFolders : 02_Areas/, personal/, scripts/

Ajouté :
  vault-config.json (schéma xais-brain v0.2)
  memory/README.md
  .claude/hooks/ (session-init + skill-discovery, +x)
  .claude/output-styles/coach.md
  .claude/settings.json
  4 skills xais-brain manquants : humanise, import-vault, inbox-zero, memory-add

Prochaines étapes :
  → /vault-setup pour personnaliser CLAUDE.md (rôle, priorités, style)
  → /daily pour démarrer ta journée
  → /inbox-zero pour trier l'inbox
```
</phase_4_validation>

<edge_cases>
**Pas de `.obsidian/`** : warning "Ce dossier ne ressemble pas à un vault Obsidian. Continuer quand même ?" via AskUserQuestion (oui/non). Si non → abort.

**Déjà adopté** (`vault-config.json` présent avec `adoptedVault: true`) : demander "Régénérer la config ?" via AskUserQuestion avant tout writing. Si non → abort sans modification.

**Aucun candidat pour un rôle** : proposer "Utiliser le standard (créer si absent)" ou "Skip". Le fallback par nom (phase 1 étape C) doit avoir minimisé ce cas.

**Vault vide** (zéro `.md`) : continuer normalement, afficher un warning et recommander `/vault-setup` en post-adoption pour personnaliser le CLAUDE.md.

**`memory.md` fichier racine** : jamais écrasé. Note ajoutée dans le nouveau `CLAUDE.md` avec la commande de migration manuelle.

**Skills custom détectés** (ex : `/client`, `/project`) : listés dans `vault-config.json.customSkills` et documentés dans la section "Slash commands — Custom (préservés)" du nouveau `CLAUDE.md`. Leur dossier `.claude/skills/[name]/` n'est jamais touché.

**`.claude/settings.json` existant** : skip la copie, warning affiché, l'utilisateur gère le merge manuel. Le skill ne fusionne pas de JSON automatiquement.

**Dossiers perso non-mappés** (ex : `personal/`, `clients/`, `scripts/`) : listés dans `vault-config.json.customFolders` et documentés dans la section structure du nouveau `CLAUDE.md`.

**Skill xais-brain déjà présent en version custom** (ex : le vault a son propre `daily/`) : respecté, pas écrasé. Message d'information affiché pour l'utilisateur qui peut comparer et migrer manuellement.

**Rollback** : pas automatique. L'utilisateur restaure son CLAUDE.md via le backup horodaté, ou restaure tout le vault via le `cp -r` recommandé dans le quick_start.
</edge_cases>

<success_criteria>
L'adoption est considérée réussie quand **toutes** les conditions suivantes sont vraies :

- `vault-config.json` existe, est du JSON valide, contient `adoptedVault: true`, `customFolders: [...]`, `customSkills: [...]`, et `folders` mappe correctement chaque rôle configuré
- `memory/` existe comme dossier ; `memory/README.md` existe (sauf s'il était déjà présent)
- Si `CLAUDE.md` existait, un backup horodaté `CLAUDE.md.backup-YYYY-MM-DD-HHMMSS` est présent à la racine
- Le nouveau `CLAUDE.md` documente le mapping réel (avec alias non-standard explicites) et liste les slash commands custom préservés dans une section dédiée
- Tous les hooks dans `.claude/hooks/*.sh` sont exécutables (`+x`)
- `.claude/settings.json` existe et est du JSON valide
- Tous les skills canoniques xais-brain manquants ont été ajoutés à `.claude/skills/`
- **Aucun** skill custom de l'utilisateur n'a été supprimé, écrasé ou modifié
- **Aucun** dossier de l'utilisateur n'a été supprimé ou vidé
- **Aucun** fichier de l'utilisateur n'a été écrasé sans backup
- Tous les chemins listés dans `vault-config.json.folders` existent effectivement sur disque
</success_criteria>
