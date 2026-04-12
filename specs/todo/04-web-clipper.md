# Piste 4 — Web Clipper pour inbox

> Priorite : MOYENNE | Effort : ~2h | Dependances : Piste 1 (vault-cli) pour `xb clip`

## Probleme

Le seul moyen d'injecter du contenu externe dans le vault est `/file-intel` (PDF, DOCX, TXT, MD) ou le copier-coller manuel. Pas de moyen de clipper une page web directement dans `inbox/`. L'utilisateur doit manuellement copier-coller le contenu ou passer par un outil tiers.

## Objectif

Permettre de clipper une URL web en une note Markdown propre dans `inbox/`, soit via le CLI (`xb clip <url>`), soit via un bookmarklet, soit via un skill Claude Code (`/clip <url>`).

---

## Phase A : Script Python `web_clip.py`

### Fichier : `scripts/web_clip.py` (nouvelle creation)

Extracteur web → Markdown, sans dep lourde. Utilise le skill Defuddle (Kepano) comme inspiration mais en standalone Python.

### Approche : `httpx` + heuristiques HTML

```python
#!/usr/bin/env python3
"""web_clip — Extrait le contenu principal d'une URL en Markdown propre.

Usage :
    python3 web_clip.py <url> <dossier_inbox>

Genere :
    inbox/<slug-du-titre>.md avec frontmatter Obsidian
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import httpx
from html.parser import HTMLParser


class ContentExtractor(HTMLParser):
    """Extracteur minimaliste : garde <p>, <h1-h6>, <li>, <blockquote>,
    ignore <nav>, <footer>, <aside>, <script>, <style>."""

    SKIP_TAGS = {"nav", "footer", "aside", "script", "style", "header", "noscript", "form"}
    BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre", "code"}

    def __init__(self):
        super().__init__()
        self.result: list[str] = []
        self.current_text: list[str] = []
        self.skip_depth = 0
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.flush_text()
            self.current_text.append("#" * level + " ")

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
        if tag == "title":
            self.in_title = False
        if tag in self.BLOCK_TAGS:
            self.flush_text()

    def handle_data(self, data):
        if self.in_title and not self.title:
            self.title = data.strip()
        if self.skip_depth == 0:
            self.current_text.append(data)

    def flush_text(self):
        text = "".join(self.current_text).strip()
        if text:
            self.result.append(text)
        self.current_text = []

    def get_markdown(self) -> str:
        self.flush_text()
        return "\n\n".join(self.result)


def fetch_and_extract(url: str) -> tuple[str, str]:
    """Fetch une URL et retourne (title, markdown_content)."""
    resp = httpx.get(url, follow_redirects=True, timeout=15,
                     headers={"User-Agent": "xais-brain-clipper/1.0"})
    resp.raise_for_status()

    extractor = ContentExtractor()
    extractor.feed(resp.text)
    title = extractor.title or urlparse(url).netloc
    content = extractor.get_markdown()
    return title, content


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", slug).strip("-")[:80] or "clip"


def clip(url: str, inbox_dir: Path) -> Path:
    """Clippe une URL dans inbox_dir et retourne le path du fichier."""
    title, content = fetch_and_extract(url)
    today = date.today().isoformat()

    frontmatter = f"""---
source: {url}
clipped: {today}
type: web-clip
tags: [inbox, web]
---"""

    markdown = f"""{frontmatter}

# {title}

> Source : [{urlparse(url).netloc}]({url}) | Clippe le {today}

{content}
"""

    inbox_dir.mkdir(parents=True, exist_ok=True)
    out_path = inbox_dir / f"{slugify(title)}.md"

    # Eviter ecrasement si fichier existe
    if out_path.exists():
        out_path = inbox_dir / f"{slugify(title)}-{today}.md"

    out_path.write_text(markdown, encoding="utf-8")
    return out_path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage : web_clip.py <url> <dossier_inbox>", file=sys.stderr)
        return 2

    url = sys.argv[1]
    inbox_dir = Path(sys.argv[2]).expanduser().resolve()

    try:
        out = clip(url, inbox_dir)
        print(f"Clippe dans {out}")
        return 0
    except httpx.HTTPError as e:
        print(f"Erreur HTTP : {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### Dependance supplementaire

Ajouter dans `requirements.txt` :

```
httpx>=0.27.0
```

**Note** : `httpx` est un choix delibere — il est deja recommande dans les conventions FastAPI, il est async-capable, et il remplace `requests` avec une meilleure API. Pas de BeautifulSoup — l'extracteur maison avec `HTMLParser` stdlib suffit pour le MVP. Si la qualite d'extraction est insuffisante, migrer vers `defuddle` (Kepano) ou `readability-lxml` en v2.

---

## Phase B : Integration CLI (`xb clip`)

### Ajout dans `vault-cli.sh`

```bash
cmd_clip() {
  local vault="$(resolve_vault)"
  local url="$1"
  if [ -z "$url" ]; then
    echo "Usage : xb clip <url>" >&2
    return 1
  fi
  local inbox_dir
  inbox_dir=$(python3 -c "import json; print(json.load(open('$vault/vault-config.json')).get('folders',{}).get('inbox','inbox'))" 2>/dev/null || echo "inbox")
  "$HOME/.xais-brain-venv/bin/python3" "$vault/scripts/web_clip.py" "$url" "$vault/$inbox_dir"
}
```

---

## Phase C : Skill Claude Code `/clip`

### Fichier : `vault-template/.claude/skills/clip/SKILL.md` (nouvelle creation)

```markdown
---
name: clip
description: Clippe une page web dans inbox/ en note Markdown propre. Utiliser quand l'utilisateur dit clip, sauvegarde cette page, clippe cette URL, web clip, ou donne une URL a sauvegarder.
user-invocable: true
disable-model-invocation: false
model: haiku
---

# clip

Clippe une URL web en note Markdown propre dans inbox/.

## Workflow

1. Demander l'URL si pas fournie
2. Lancer le script Python :
   ```bash
   ~/.xais-brain-venv/bin/python3 scripts/web_clip.py "<url>" "<inbox_dir>"
   ```
3. Lire le fichier genere pour confirmer le contenu
4. Proposer /inbox-zero pour trier

## Edge cases

- Si l'URL est un PDF → rediriger vers /file-intel
- Si l'extraction est vide → warning, proposer de copier-coller manuellement
- Si le fichier existe deja → le script ajoute la date au nom
```

---

## Phase D : Bookmarklet (bonus, optionnel)

Un bookmarklet JavaScript qui envoie l'URL courante au vault via un serveur local minimaliste. **Hors scope MVP** — a documenter comme piste future dans le README.

Idee d'implementation future :

```javascript
// Bookmarklet — necessite un serveur local xb serve (port 19384)
javascript:void(fetch('http://localhost:19384/clip',{method:'POST',body:JSON.stringify({url:location.href,title:document.title})}))
```

---

## Fichiers a creer/modifier

| Fichier | Action |
|---------|--------|
| `scripts/web_clip.py` | **CREER** — extracteur web (~100 lignes) |
| `vault-template/.claude/skills/clip/SKILL.md` | **CREER** — skill Claude Code |
| `vault-cli.sh` | **MODIFIER** — ajouter commande `clip` |
| `requirements.txt` | **MODIFIER** — ajouter `httpx>=0.27.0` |
| `setup.sh` | **MODIFIER** — copier `web_clip.py` dans le vault, ajouter `clip` a la skills list (10 → 11) |
| `vault-template/CLAUDE.md` | **MODIFIER** — ajouter `/clip` a la liste des slash commands |
| `README.md` | **MODIFIER** — documenter `/clip` et `xb clip` |

## Tests

### `tests/test_web_clip.py`

```python
"""Tests pour web_clip.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from web_clip import slugify, ContentExtractor


def test_slugify():
    assert slugify("Mon Article - Le Monde") == "mon-article-le-monde"

def test_slugify_long():
    long_title = "A" * 200
    assert len(slugify(long_title)) <= 80

def test_extractor_basic():
    html = "<html><title>Test</title><body><p>Hello world</p></body></html>"
    ext = ContentExtractor()
    ext.feed(html)
    assert ext.title == "Test"
    assert "Hello world" in ext.get_markdown()

def test_extractor_skips_nav():
    html = "<nav>Menu</nav><p>Content</p><footer>Footer</footer>"
    ext = ContentExtractor()
    ext.feed(html)
    md = ext.get_markdown()
    assert "Content" in md
    assert "Menu" not in md
    assert "Footer" not in md

def test_extractor_headings():
    html = "<h2>Titre</h2><p>Texte</p>"
    ext = ContentExtractor()
    ext.feed(html)
    md = ext.get_markdown()
    assert "## Titre" in md
```

## Criteres de succes

- [ ] `python3 web_clip.py <url> /tmp/inbox` genere un .md propre avec frontmatter
- [ ] L'extraction HTML supprime nav/footer/scripts
- [ ] Le frontmatter contient source, date, type, tags
- [ ] `xb clip <url>` fonctionne depuis n'importe quel dossier
- [ ] `/clip` dans Claude Code lance le script et confirme
- [ ] Les URLs en erreur (404, timeout) sont gerees proprement
- [ ] Pas d'ecrasement si le fichier existe deja
