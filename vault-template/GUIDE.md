# GUIDE — Mon Second Cerveau

> Guide didactique pour l'utilisateur. Pour les instructions que Claude suit quand il ouvre ton vault, voir [CLAUDE.md](CLAUDE.md).

---

## 1. Bienvenue

**xais-brain** est un vault Obsidian piloté par Claude Code. Tes notes restent en Markdown brut sur ton disque, et Claude les lit, les enrichit et diagnostique leur santé via des *slash commands* (`/vault-audit`, `/daily`, `/clip`…) ou la CLI `xb`.

Tu n'as rien à apprendre d'Obsidian au-delà de "double-cliquer sur un fichier". Tout le reste se pilote en langage naturel dans Claude Code.

Ce guide t'explique **quand** utiliser chaque skill, un workflow quotidien type, et comment personnaliser le système. Pour l'installation et la narrative produit : voir [README sur GitHub](https://github.com/XAISOLUCES/xais-brain/blob/main/README.md).

---

## 2. Quand utiliser quel skill

| Tu veux… | Commande | Note |
|---|---|---|
| Démarrer ta journée avec le contexte du vault | `/daily` | Crée `daily/YYYY-MM-DD.md` si absent |
| Sauver un résumé de la session courante | `/tldr` | Choisit le dossier de destination automatiquement |
| Clipper une page web dans ton vault | `/clip <url>` ou `xb clip <url>` | Produit une note propre dans `inbox/` |
| Digérer un dossier de PDFs / DOCX | `/file-intel` ou `xb intel <dir>` | Annonce le budget, demande validation avant batch |
| Trier `inbox/` dans les bons dossiers | `/inbox-zero` ou `xb inbox` | Propose un plan numéroté, attend un go |
| Auditer la santé du vault | `/vault-audit` ou `xb audit` | Génère `99-Meta/Audit-YYYY-MM-DD.md` |
| Compléter les frontmatter des vieilles notes | `xb audit --migrate` | Additif, n'écrase jamais |
| Ajouter une mémoire long terme | `/memory-add` | Met à jour `MEMORY.md` automatiquement |
| Charger le contexte d'un side-project | `/project` | Lit `projects/[nom]/` |
| Charger le contexte d'un client en prod | `/client` | Lit `clients/[nom]/` |
| Nettoyer un texte AI-ifié (voix naturelle FR) | `/humanise` | Passe sur le texte fourni |
| Personnaliser ce vault (rôle, projets) | `/vault-setup` | Réécrit `CLAUDE.md` via interview |
| Adopter un vault Obsidian existant | `/import-vault` | Ne casse pas la structure existante |

Règle simple : si tu hésites entre deux commandes, lance-les via leur nom en français dans Claude Code, il saura déclencher la bonne.

---

## 3. Workflow quotidien type

Une journée typique :

**Matin — démarrage (~1 min)**

```
/daily
```

Claude lit `daily/<aujourd'hui>.md` (ou le crée), vérifie l'inbox, te rappelle les priorités récentes. Tu repars avec ta note du jour ouverte.

**En travaillant**

- Tu tombes sur un article intéressant → `/clip <url>` ou `xb clip <url>`. La note atterrit dans `inbox/` avec un frontmatter complet et une entrée dans `99-Meta/Fact-Check-Log.md`.
- Tu reçois un dossier de PDFs à digérer → `xb intel ~/Downloads/pdfs`. La commande annonce le nombre de pages, l'estimation de coût, demande un go, puis produit un résumé Markdown par fichier dans `inbox/`.
- Tu changes d'avis, tu apprends quelque chose qui mérite d'être retenu → `/memory-add`.

**Fin de journée — archivage (~2 min)**

```
/tldr
/inbox-zero
```

`/tldr` sauvegarde un résumé de la session. `/inbox-zero` te propose un plan de tri numéroté (fichier → dossier) et attend ta validation avant d'exécuter. Tu confirmes par "ok" ou tu corriges ("1→archive, 3→research").

**Une fois par mois — hygiène**

```
xb audit
```

Rapport complet : orphelines, anémiques, doublons, frontmatter incomplet, `to-verify` qui traînent, tags incohérents, wikilinks cassés. Tu coches les cases, tu résous au fur et à mesure.

---

## 4. Traiter de nouveaux fichiers

Trois points d'entrée selon la source.

### Une page web

```bash
xb clip https://exemple.com/article
```

Produit `inbox/<titre-slugifié>.md` avec :

```yaml
---
source: web
source_url: https://exemple.com/article
source_knowledge: web-checked
verification_date: <aujourd'hui>
statut: draft
importance: medium
---
```

Append automatique dans `99-Meta/Fact-Check-Log.md` (date, lien, skill, statut).

### Des fichiers locaux (PDF, DOCX, TXT, MD)

```bash
xb intel ~/Documents/articles-a-lire
```

Phases :

1. Listing + estimation budget (pages totales, temps, coût selon `LLM_PROVIDER`).
2. **Checkpoint** : Claude attend "oui" pour lancer.
3. Traitement des 2-3 premiers fichiers, résumé visible, nouveau checkpoint.
4. Batch complet, résumés dans `inbox/`, entrées dans `Fact-Check-Log.md`.

Pour bypasser les checkpoints (CI, scripts) : `XAIS_BRAIN_CI=1 xb intel <dir>`.

### Des fichiers déjà dans `inbox/`

```
/inbox-zero
```

Claude liste tout, propose un plan de tri numéroté (source → destination), attend ton go, puis déplace. Respecte tout frontmatter existant — il ne réécrit jamais les champs déjà remplis.

---

## 5. Mémoire long terme

Deux niveaux de mémoire se combinent :

**`MEMORY.md`** (racine) — index des topics mémoire. Court, toujours chargé par Claude.

**`memory/`** (dossier) — les fichiers détaillés (`user.md`, `projects.md`, `decisions.md`, `preferences.md`…). Chargés **uniquement quand pertinents** grâce au pattern natif Claude Code.

### Ajouter une mémoire

```
/memory-add
```

Claude te demande quoi retenir, choisit la bonne catégorie (décision produit, préférence workflow, pattern récurrent…), crée ou enrichit le fichier approprié dans `memory/`, met à jour `MEMORY.md`.

### Consulter la mémoire

Claude la lit tout seul quand le contexte l'exige. Tu peux aussi ouvrir `MEMORY.md` pour un coup d'œil rapide.

---

## 6. Projets et clients

Deux slash commands pour charger le contexte complet d'un chantier :

### `/project`

Pour tes side-projects et explorations persos. Lit tout `projects/[nom]/` : README, notes récentes, statut, décisions, next actions. Utilise-la en début de session quand tu reprends un projet après une pause.

### `/client`

Pour tes clients en prod. Lit `clients/[nom]/` : briefs, specs, historique des échanges, tickets. Parfait quand une demande entrante tombe et que tu dois te remettre dans le contexte rapidement.

### Organiser ces dossiers

Minimum recommandé par projet/client :

```
projects/mon-projet/
├── README.md          ← vue d'ensemble, statut, next actions
├── decisions.md       ← décisions importantes datées
└── notes/             ← notes de session, brainstorms
```

Pas obligatoire — Claude s'adapte à ce qu'il trouve. Mais un `README.md` en tête aide énormément à la reprise.

---

## 7. Hygiène du vault

Tous les PKM rouillent : orphelines, doublons, liens cassés, frontmatter incomplet. Sans audit, tu ne le vois qu'après des mois. **`xb audit`** scanne 7 symptômes :

| Détection | Ce que ça veut dire |
|---|---|
| Notes orphelines | 0 backlinks ET 0 wikilinks sortants — note isolée du reste |
| Notes anémiques | < 100 mots — probablement un brouillon oublié |
| Doublons (titre exact) | Même titre dans deux dossiers — à fusionner ou archiver |
| Frontmatter incomplet | Manque `statut` ou `source_knowledge` — note non auditable |
| `to-verify` > 30 jours | Note marquée "à vérifier" mais jamais revisitée |
| Tags incohérents | `#ai` + `#AI` + `#ia` — à unifier |
| Wikilinks cassés | `[[X]]` où `X.md` n'existe pas |

### Usage

```bash
xb audit                 # Rapport seulement
xb audit --migrate       # Rapport + complète les frontmatter manquants
xb audit --json          # Sortie JSON (scripting)
xb audit --output <file> # Rapport vers un chemin custom
```

Output par défaut : `99-Meta/Audit-YYYY-MM-DD.md` — checklist Markdown actionnable.

Rythme conseillé : une fois par mois, ou dès que ton vault dépasse 100 notes.

> `99-Meta/` est la **piste d'audit** du vault. À exclure du graphe Obsidian (Settings → Files & Links → Excluded files → ajouter `99-Meta/`) pour que ces fichiers ne polluent pas la graph view.

---

## 8. Personnalisation

Trois leviers, du plus léger au plus profond.

### 8.1 `CLAUDE.md`

C'est le fichier que Claude lit en premier quand il ouvre ton vault. Après l'install, il est générique. Lance :

```
/vault-setup
```

Claude t'interviewe en 4 questions (rôle, projets actifs, objectifs, style) puis réécrit `CLAUDE.md` sur mesure. Tu peux aussi l'éditer à la main à tout moment.

### 8.2 `.claude/rules/` — règles avancées

Tu veux imposer un ton de voix, une convention de nommage, une taxonomie de tags ? Crée un fichier dans `.claude/rules/` puis importe-le dans `CLAUDE.md` :

```markdown
@import .claude/rules/voice.md
@import .claude/rules/naming.md
@import .claude/rules/daily-template.md
```

Avantage : `CLAUDE.md` reste léger, les règles spécialisées ne sont chargées **que quand pertinentes**.

### 8.3 Mode Coach FR

```
/output-style
```

Sélectionne **Coach FR** : Claude passe en mode coaching, questions challengeantes, focus action. Chaque réponse se termine par une action faisable dans l'heure et une question. Pour revenir : `/output-style` → `default`.

### 8.4 Ajouter ta propre skill

```bash
mkdir -p ~/.claude/skills/ma-commande
cat > ~/.claude/skills/ma-commande/SKILL.md << 'EOF'
---
name: ma-commande
description: Ce que fait ma commande et quand l'utiliser.
user-invocable: true
model: haiku
---

# ma-commande

[Instructions pour Claude quand cette commande est appelée]
EOF
```

Elle sera dispo via `/ma-commande` dans Claude Code.

---

## 9. CLI `xb`

Le setup installe `xb` dans `~/.local/bin/` — utilisable depuis n'importe quel dossier.

```bash
xb daily                      # /daily en one-shot
xb inbox                      # /inbox-zero en one-shot
xb intel <dossier>            # Traite des fichiers via LLM (pas besoin de Claude Code)
xb clip <url>                 # Clippe une page web dans inbox/
xb audit [--migrate]          # Rapport d'hygiène du vault
xb status                     # État du vault (inbox, daily, provider)
xb open                       # Ouvre Obsidian sur le vault
xb shell                      # Ouvre Claude Code interactif dans le vault
xb help                       # Liste toutes les commandes
xb version                    # Version installée
```

### Résolution du vault

`xb` cherche dans cet ordre :

1. **`$XAIS_BRAIN_VAULT`** (variable d'env) — prioritaire
2. **`vault-config.json`** dans le répertoire courant
3. **`~/xais-brain-vault/`** (défaut)

Multi-vaults :

```bash
XAIS_BRAIN_VAULT=~/vault-client-A xb status
XAIS_BRAIN_VAULT=~/vault-perso xb daily
```

### Mode CI / scripts

```bash
XAIS_BRAIN_CI=1 xb intel ~/docs
```

Bypasse les checkpoints interactifs (stdin bloquant). Utile pour cron, CI, automatisations.

---

## 10. FAQ

**Mes notes sont-elles uploadées quelque part ?**
Non. Le vault reste sur ton disque. Les seuls appels réseau sont vers l'API LLM que tu as configurée (`LLM_PROVIDER` dans `.env`) pour `/file-intel`, `/clip` et les skills conversationnels.

**Puis-je utiliser un vault Obsidian existant ?**
Oui. Lance `claude` depuis la racine de ton vault existant puis `/import-vault`. xais-brain s'installe par-dessus sans casser ta structure.

**Je veux changer de provider LLM — je dois tout réinstaller ?**
Non. Édite `~/xais-brain-vault/.env` : `LLM_PROVIDER=gemini` (ou `claude`, `openai`). Aucun code à toucher.

**Comment j'ajoute plusieurs vaults sur ma machine ?**
Crée un autre dossier avec son propre `vault-config.json` (copie celui du template). Appelle `xb` avec `XAIS_BRAIN_VAULT=<chemin>` ou `cd` dans le vault et lance `xb` — il détecte le `vault-config.json` du `cwd`.

**Les hooks ralentissent Claude Code ?**
Non. `SessionStart` = 3 lignes max (vault name, date, inbox count). `UserPromptSubmit` = silencieux sauf si ton message contient un mot-clé FR (`skill`, `commandes`, `aide-moi`…). Aucun appel LLM dans les hooks.

**Pourquoi `99-Meta/` ? Je peux le supprimer ?**
C'est la **piste d'audit** : rapports d'audit, log des sources vérifiées, debriefs de session. Si tu le supprimes, tu perds la traçabilité. Exclus-le du graphe Obsidian plutôt (Settings → Files & Links → Excluded files → `99-Meta/`) — il reste visible dans le file explorer mais ne pollue plus la graph view.

**Je peux utiliser xais-brain sans Claude Code ?**
Partiellement. `xb intel`, `xb clip` et `xb audit` tournent en pur Python. `xb daily`, `xb inbox`, `xb shell` nécessitent Claude Code installé (`curl -fsSL https://claude.ai/install.sh | sh`).

**Comment je fais une sauvegarde du vault ?**
Le vault est un dossier de Markdown brut — copie-le, committe-le dans git, pousse-le dans un repo privé. Pas de DB, pas de format propriétaire.

**Ça marche sous Windows ?**
Supporté officiellement : macOS et Linux. Sous Windows, tente WSL2 avec Ubuntu — le `setup.sh` devrait fonctionner, mais ce n'est pas testé en CI.

**Un frontmatter incomplet casse `/vault-audit` ?**
Non, c'est un warning non-bloquant. L'audit tourne quand même et liste les notes concernées dans la section "Frontmatter incomplet". Lance `xb audit --migrate` pour compléter automatiquement avec des valeurs par défaut (sans écraser ce qui existe).

---

## Pour aller plus loin

- **Narrative produit et installation** : [README sur GitHub](https://github.com/XAISOLUCES/xais-brain/blob/main/README.md)
- **Arborescence complète et flux** : [ARCHITECTURE sur GitHub](https://github.com/XAISOLUCES/xais-brain/blob/main/ARCHITECTURE.md)
- **Règles de chargement de contexte Claude** : [CLAUDE.md](CLAUDE.md)
- **Index mémoire** : [MEMORY.md](MEMORY.md)

Bug ou idée ? [GitHub Issues](https://github.com/XAISOLUCES/xais-brain/issues).
