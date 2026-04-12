# Piste 5 — Demo GIF pour le README

> Priorite : BASSE (cosmetic mais fort impact marketing) | Effort : ~30min | Dependances : Piste 2 (CI) et Piste 1 (vault-cli) idealement terminees

## Probleme

Le README n'a aucun visuel. Un repo GitHub sans demo visuelle perd ~70% des visiteurs dans les 5 premieres secondes. xais-brain est un outil CLI/TUI interactif — un GIF de demo est le format ideal pour montrer le flow en action.

## Objectif

Creer 1-2 GIFs animes (ou un screencast) montrant le workflow principal de xais-brain, et les integrer dans le README.

---

## Contenu des demos

### Demo 1 : Setup en 60 secondes (GIF principal)

**Scenario :**
1. Terminal vide
2. `curl ... | bash` → banniere xais-brain apparait
3. Path du vault : Entree (defaut)
4. LLM : 1 (Gemini)
5. Coller une cle API (fake, masquee)
6. Skip import
7. Skip Kepano
8. Resume final : "10 skills installes"
9. Obsidian s'ouvre

**Duree cible : 15-20 secondes** (accelere 3-4x).

### Demo 2 : Session Claude Code (GIF secondaire)

**Scenario :**
1. `cd ~/mon-vault && claude`
2. Hook `session-init` affiche le contexte
3. User tape `/daily` → Claude genere la note du jour
4. User tape "quels skills ?" → hook `skill-discovery` liste les commands
5. User tape `/inbox-zero` → Claude trie l'inbox

**Duree cible : 20-25 secondes** (accelere 2x).

### Demo 3 (optionnel) : `xb` CLI one-liners

**Scenario :**
1. `xb status` → affiche l'etat du vault
2. `xb intel ~/Documents` → traite un PDF
3. `xb clip https://example.com/article` → clippe une page web

**Duree cible : 10 secondes.**

---

## Outils recommandes

### Option A : VHS (Charm) — **recommandee**

[VHS](https://github.com/charmbracelet/vhs) de Charm genere des GIFs a partir de scripts `.tape`. Deterministe, reproductible, pas besoin de screen recording manuel.

```bash
brew install vhs
```

### Fichier : `demo/setup.tape` (nouvelle creation)

```tape
# xais-brain setup demo
Output demo/setup.gif
Set FontSize 14
Set Width 900
Set Height 500
Set Theme "Catppuccin Mocha"

Type "curl -fsSL https://raw.githubusercontent.com/XAISOLUCES/xais-brain/main/setup.sh | bash"
Enter
Sleep 2s

# Simule les reponses
Type ""
Enter
Sleep 1s
Type "1"
Enter
Sleep 500ms
Type "AIzaSyFakeKeyForDemo1234567890"
Enter
Sleep 500ms
Type ""
Enter
Sleep 500ms
Type "n"
Enter
Sleep 3s
```

**Limitation VHS** : VHS execute vraiment les commandes. Pour la demo, il faut soit :
- Utiliser le mode CI (`XAIS_BRAIN_CI=true`) avec des valeurs pre-remplies
- Ou scripter un setup.sh "fake" qui ne fait que l'affichage

### Option B : asciinema + acast/svg-term

```bash
asciinema rec demo/setup.cast --cols 100 --rows 30
# ... faire la demo manuellement
svg-term --in demo/setup.cast --out demo/setup.svg --window
```

Avantage : le SVG est plus net qu'un GIF. Inconvenient : pas reproductible sans rejouer.

### Option C : Screen recording + gifski

```bash
# Enregistrer avec OBS ou QuickTime
# Convertir en GIF optimise
gifski --fps 10 --width 800 -o demo/setup.gif recording.mov
```

---

## Integration README

### Positionnement dans le README

Le GIF doit etre **tout en haut**, entre le badge et la description :

```markdown
# xais-brain

> Ton second cerveau — Obsidian + Claude Code, pret en une commande.

[![License: MIT](...)](#)

![xais-brain setup demo](demo/setup.gif)

**xais-brain** est un installateur tout-en-un...
```

### Taille du fichier

- **Cible : < 2 MB** par GIF (GitHub affiche mal les GIFs > 5 MB)
- Utiliser `gifsicle --optimize=3` ou `gifski --quality 80` pour comprimer
- Alternative : heberger sur un CDN (mais moins fiable a long terme que le repo)

---

## Fichiers a creer/modifier

| Fichier | Action |
|---------|--------|
| `demo/setup.tape` | **CREER** — script VHS pour la demo setup |
| `demo/session.tape` | **CREER** — script VHS pour la demo session Claude |
| `demo/setup.gif` | **GENERER** — via VHS ou screen recording |
| `demo/session.gif` | **GENERER** — via VHS ou screen recording |
| `README.md` | **MODIFIER** — ajouter les GIFs en haut du fichier |
| `.gitignore` | **MODIFIER** — ajouter `demo/*.cast` (fichiers intermediaires asciinema) |

## Contraintes

- **Pas de vraie cle API dans le GIF** — utiliser une fausse cle ou masquer la saisie
- **Pas de donnees personnelles** — utiliser un vault vide avec des noms generiques
- **Reproductible** — privilegier VHS (tape scripts) pour pouvoir regenerer apres chaque changement de UI
- **Compression** — chaque GIF < 2 MB, total demo/ < 5 MB pour ne pas bloater le clone

## Criteres de succes

- [ ] Au moins 1 GIF visible dans le README sans scroll
- [ ] Le GIF montre le flow complet setup (banniere → skills installes)
- [ ] Fichier < 2 MB, lisible sur GitHub
- [ ] Pas de donnees sensibles visibles
- [ ] Script VHS ou equivalent reproductible versionne dans `demo/`
