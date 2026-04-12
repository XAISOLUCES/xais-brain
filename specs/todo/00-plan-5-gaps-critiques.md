# Plan maitre — 5 gaps critiques xais-brain

> Date : 2026-04-12
> Auteur : session brainstorm → plan
> Statut : PRET A BUILDER

## Vue d'ensemble

5 pistes d'amelioration identifiees par le brainstorm, ordonnees par priorite et dependances optimisees.

## Ordre d'execution

```
Piste 1 (vault-cli.sh)  ─────────────────┐
   ~1h, aucune dep                        │
                                          ├──→ Piste 4 (web clipper)
Piste 2 (CI + tests + non-interactif) ───┤       ~2h, dep Piste 1 (xb clip)
   ~2h, aucune dep                        │
                                          ├──→ Piste 3 (Linux)
                                          │       ~1.5h, dep Piste 2 (CI pour valider)
                                          │
                                          └──→ Piste 5 (demo GIF)
                                                  ~30min, dep Piste 1+2 idealement
```

### Parallelisme possible

- **Piste 1 et Piste 2** sont independantes → peuvent etre buildees en parallele
- **Piste 3** depend de Piste 2 (le CI doit tourner pour valider Linux)
- **Piste 4** depend de Piste 1 (le CLI `xb clip` etend vault-cli.sh)
- **Piste 5** est le dernier step (les GIFs doivent montrer le produit final)

## Resume par piste

| # | Piste | Effort | Priorite | Spec detaillee |
|---|-------|--------|----------|----------------|
| 1 | **vault-cli.sh** — CLI wrapper `xb` | ~1h | HAUTE | [01-vault-cli-wrapper.md](01-vault-cli-wrapper.md) |
| 2 | **CI + tests + non-interactif** — mode CI, tests bash+Python, GitHub Actions | ~2h | HAUTE | [02-ci-tests-non-interactif.md](02-ci-tests-non-interactif.md) |
| 3 | **Support Linux** — setup.sh portable macOS+Linux | ~1.5h | MOYENNE | [03-support-linux.md](03-support-linux.md) |
| 4 | **Web clipper** — `xb clip` + `/clip` + `web_clip.py` | ~2h | MOYENNE | [04-web-clipper.md](04-web-clipper.md) |
| 5 | **Demo GIF** — screencast anime dans le README | ~30min | BASSE | [05-demo-gif-readme.md](05-demo-gif-readme.md) |

## Impact attendu

| Piste | Impact utilisateur | Impact dev |
|-------|-------------------|------------|
| 1 - vault-cli | UX : operations courantes sans ouvrir Claude | Fondation pour les futures commandes |
| 2 - CI/tests | Qualite : plus de bugs de docs, regression catch | Dev : confiance pour refactorer |
| 3 - Linux | Portee : ~50% de la cible potentielle debloquee | CI valide automatiquement |
| 4 - Web clipper | UX : clipper web → inbox en 1 commande | Nouveau skill + extension CLI |
| 5 - Demo GIF | Marketing : conversion visiteurs README x3-5 | Reproductible via VHS |

## Fichiers touches (vue consolidee)

### Nouveaux fichiers

| Fichier | Piste |
|---------|-------|
| `vault-cli.sh` | 1 |
| `tests/test_setup.sh` | 2 |
| `tests/test_file_intel.py` | 2 |
| `.github/workflows/ci.yml` | 2 |
| `scripts/web_clip.py` | 4 |
| `vault-template/.claude/skills/clip/SKILL.md` | 4 |
| `tests/test_web_clip.py` | 4 |
| `demo/setup.tape` | 5 |
| `demo/setup.gif` | 5 |

### Fichiers modifies

| Fichier | Pistes |
|---------|--------|
| `setup.sh` | 1, 2, 3, 4 |
| `README.md` | 1, 3, 4, 5 |
| `vault-template/CLAUDE.md` | 4 |
| `requirements.txt` | 4 |
| `.gitignore` | 5 |

## Risques transversaux

1. **`setup.sh` est touche par 4 pistes** — risque de conflits si buildees en parallele. Solution : merger Piste 1 et 2 d'abord, puis 3 et 4 sequentiellement.

2. **Skills count drift** — chaque ajout de skill (clip = 11e) necessite de mettre a jour 4 endroits dans `setup.sh`. Le risque de handoff 006 se repete. Solution : le mode CI (Piste 2) avec son test `skill_count == N` detectera automatiquement le drift.

3. **`httpx` comme nouvelle dep** (Piste 4) — ajoute ~2 MB au venv. Acceptable car c'est une dep standard Python, deja dans les conventions du projet.

4. **VHS pour les GIFs** (Piste 5) — necessite l'execution reelle de `setup.sh`. Le mode CI (Piste 2) est un prerequis pratique pour que VHS puisse scripter le setup sans intervention humaine.

## Session de build recommandee

### Session 1 (~3h) : Fondations

1. Builder **Piste 2** (CI + tests + non-interactif) — c'est le socle
2. Builder **Piste 1** (vault-cli.sh) — rapide, impact immediat
3. Commit + push + verifier que CI passe

### Session 2 (~2h) : Extensions

4. Builder **Piste 3** (Linux) — debloquer le CI Linux
5. Builder **Piste 4** (web clipper) — nouveau skill + CLI
6. Commit + push + verifier que CI passe macOS + Linux

### Session 3 (~30min) : Polish

7. Builder **Piste 5** (demo GIF) — necessite le produit quasi-final
8. Commit final + push

## Commande de build

```
/XD-build specs/todo/01-vault-cli-wrapper.md
/XD-build specs/todo/02-ci-tests-non-interactif.md
/XD-build specs/todo/03-support-linux.md
/XD-build specs/todo/04-web-clipper.md
/XD-build specs/todo/05-demo-gif-readme.md
```

Ou pour tout enchainer en une session :

```
/XD-build specs/todo/00-plan-5-gaps-critiques.md
```
