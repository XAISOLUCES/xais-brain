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
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import httpx


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
    resp = httpx.get(
        url,
        follow_redirects=True,
        timeout=15,
        headers={"User-Agent": "xais-brain-clipper/1.0"},
    )
    resp.raise_for_status()

    extractor = ContentExtractor()
    extractor.feed(resp.text)
    title = extractor.title or urlparse(url).netloc
    content = extractor.get_markdown()
    return title, content


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", slug).strip("-")[:80] or "clip"


def build_frontmatter(url: str, today: str) -> str:
    """Construit le frontmatter enrichi (piste 6B) pour une note clippee.

    Schema cible (cf. specs/todo/06-integration-god-mode-patterns.md §3.2) :
        source: web
        source_url: <url>
        source_knowledge: web-checked
        verification_date: <today ISO>
        statut: draft
        importance: medium
        type: web-clip
        clipped: <today>
        tags: [inbox, web]
    """
    return (
        "---\n"
        "source: web\n"
        f"source_url: {url}\n"
        "source_knowledge: web-checked\n"
        f"verification_date: {today}\n"
        "statut: draft\n"
        "importance: medium\n"
        "type: web-clip\n"
        f"clipped: {today}\n"
        "tags: [inbox, web]\n"
        "---"
    )


def append_fact_check_log(vault_dir: Path, note_title: str, url: str, today: str) -> None:
    """Append une entree dans 99-Meta/Fact-Check-Log.md si le fichier existe.

    No-op si le dossier 99-Meta/ n'existe pas (vault pre-6A ou non configure).
    Piste 6D a la charge d'alimenter completement ce log, mais la piste 6B
    prepare deja les metadonnees necessaires dans le frontmatter.
    """
    log_path = vault_dir / "99-Meta" / "Fact-Check-Log.md"
    if not log_path.exists():
        return
    entry = (
        f"\n## {today} — [[{note_title}]]\n"
        f"- **Source** : web (`{url}`)\n"
        "- **Skill** : /clip\n"
        "- **Statut** : draft (à vérifier)\n"
    )
    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        # Log cassable mais non bloquant pour le clip lui-meme
        pass


def clip(url: str, inbox_dir: Path) -> Path:
    """Clippe une URL dans inbox_dir et retourne le path du fichier."""
    title, content = fetch_and_extract(url)
    today = date.today().isoformat()

    frontmatter = build_frontmatter(url, today)

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

    # Best-effort append au Fact-Check-Log si le vault l'a (piste 6A/6D)
    # inbox_dir = <vault>/inbox → parent = <vault>
    append_fact_check_log(inbox_dir.parent, title, url, today)

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
