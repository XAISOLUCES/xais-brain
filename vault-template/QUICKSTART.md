# Quickstart — xais-brain

> **Plan de test post-install + cheat-sheet quotidien.** Pour le guide détaillé, voir [GUIDE.md](GUIDE.md). Pour la narrative produit, voir [README sur GitHub](https://github.com/XAISOLUCES/xais-brain/blob/main/README.md).

---

## Plan de test — smoke test end-to-end (~15 min)

### 1. Vérifier l'install

```bash
cd ~/mon-vault            # ou ~/xais-brain-vault par défaut
xb status                 # → vault, provider LLM, inbox count, daily
xb help                   # → liste des commandes xb
ls .claude/skills         # → 12 dossiers skills
cat .env                  # → LLM_PROVIDER + clé API présents
cat .claude/pricing.json  # → 3 providers (gemini/claude/openai)
```

Si `xb: command not found` → `export PATH="$HOME/.local/bin:$PATH"` dans ton `~/.zshrc`.

### 2. `xb audit` (piste 6E + 6H)

```bash
xb audit                  # → rapport dans 99-Meta/Audit-YYYY-MM-DD.md
cat 99-Meta/Audit-*.md | head -50
```

Tu dois voir 8 sections : orphelines, anémiques, doublons, frontmatter incomplet, to-verify stale, tags incohérents, wikilinks cassés, **notes peu liées**.

```bash
xb audit --json | python3 -m json.tool | head -20   # → JSON valide
xb audit --output /tmp/audit.md                     # → écrit ailleurs
```

### 3. `/clip` (piste 6B + 6D)

Dans Claude Code dans le vault :

```
/clip https://anthropic.com
```

Puis :

```bash
ls inbox/                                  # → nouvelle note .md
head -15 inbox/anthropic-*.md              # → frontmatter enrichi
cat 99-Meta/Fact-Check-Log.md | tail -5    # → entrée append-only
```

### 4. `/file-intel` (piste 6C + 6D + 6F)

Crée 2-3 petits fichiers test :

```bash
mkdir -p /tmp/test-intel
echo "Test file 1 content." > /tmp/test-intel/a.txt
echo "Test file 2 content." > /tmp/test-intel/b.txt
xb intel /tmp/test-intel
```

Tu dois voir :

- **Budget annoncé** (piste 6F) : `"va traiter 2 fichier(s) (~2 pages). Estimation : …, gratuit (free tier) (provider: gemini)."`
- **Pas de checkpoint** (batch < 6 fichiers) (piste 6C)
- **Notes créées** dans `inbox/` avec frontmatter enrichi 6B/6H (`liens_forts`, `liens_opposition`)
- **Fact-Check-Log alimenté** (piste 6D) : `tail 99-Meta/Fact-Check-Log.md`

Pour tester le checkpoint 6C, fais un batch ≥ 6 fichiers :

```bash
for i in 1 2 3 4 5 6 7; do echo "content $i" > /tmp/test-intel/f$i.txt; done
xb intel /tmp/test-intel
# → checkpoint pre-batch : [Y/n]
# → checkpoint post-3-fichiers : [Y/n]
```

Pour bypasser en CI :

```bash
XAIS_BRAIN_CI=1 xb intel /tmp/test-intel   # → aucune interaction
```

### 5. `xb audit --migrate`

```bash
echo "# Ma note" > inbox/test-migrate.md
xb audit --migrate                         # → complète le frontmatter
head -10 inbox/test-migrate.md             # → frontmatter ajouté
```

### 6. Hooks + skills FR

Lance Claude Code (`claude`) dans le vault :

- Le hook `SessionStart` affiche en 3 lignes max : vault, date, inbox count
- Tape `quelles commandes ?` → le hook `UserPromptSubmit` liste les skills

### 7. `/vault-setup` (une fois)

```
/vault-setup
```

Interview 4 questions (rôle, projets, objectifs, style) → `CLAUDE.md` personnalisé.

### 8. `/daily` et `/tldr`

```
/daily          # → crée daily/YYYY-MM-DD.md avec contexte
/tldr           # → sauvegarde résumé de session dans le bon dossier
```

### 9. Nettoyage

```bash
rm -rf /tmp/test-intel
rm inbox/test-migrate.md inbox/anthropic-*.md inbox/f*.md inbox/a.md inbox/b.md
xb audit   # → rapport propre
```

---

## Cheat-sheet quotidien

### Matin

```
/daily                    # contexte du jour + priorités
xb status                 # inbox count, provider
```

### Pendant la journée

| Besoin | Commande |
|---|---|
| Clipper un article web | `xb clip <url>` ou `/clip <url>` dans CC |
| Traiter des PDFs/DOCX | `xb intel ~/Documents/dossier` |
| Trier l'inbox | `/inbox-zero` dans CC |
| Retenir un truc | `/memory-add` |
| Charger contexte projet | `/project nom-du-projet` |
| Charger contexte client | `/client nom-du-client` |

### Fin de journée

```
/tldr                     # sauvegarde résumé de la session
xb audit                  # bilan hygiène vault (hebdo suffit)
```

### Maintenance hebdo

```bash
xb audit                  # → ouvre 99-Meta/Audit-*.md, coche les items traités
xb audit --migrate        # → complète frontmatter oubliés
/inbox-zero               # → vide l'inbox
```

### En cas de doute

```
xb help                   # liste commandes xb
cat GUIDE.md              # guide utilisateur détaillé dans le vault
```
