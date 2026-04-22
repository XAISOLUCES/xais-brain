#!/usr/bin/env python3
"""file-intel — Traite un dossier de fichiers via LLM et génère des notes Markdown.

Usage :
    python3 file_intel.py <dossier_source> <dossier_inbox>

Variables d'environnement (lues depuis le .env du vault) :
    LLM_PROVIDER        : gemini | claude | openai (défaut: gemini)
    GOOGLE_API_KEY      : clé Gemini (si LLM_PROVIDER=gemini)
    ANTHROPIC_API_KEY   : clé Claude (si LLM_PROVIDER=claude)
    OPENAI_API_KEY      : clé OpenAI (si LLM_PROVIDER=openai)

Variables d'env optionnelles (override des modèles) :
    GEMINI_MODEL        : défaut gemini-2.0-flash
    ANTHROPIC_MODEL     : défaut claude-haiku-4-5-20251001
    OPENAI_MODEL        : défaut gpt-4o-mini
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv

# On ajoute le dossier du script au path pour pouvoir importer providers/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from providers import get_provider  # noqa: E402
from providers._prompts import source_type_from_filename  # noqa: E402
from providers.base import LLMProvider  # noqa: E402


# ── Extracteurs ───────────────────────────────────────────────────────────────


def extract_pdf(path: Path) -> str:
    """Extrait le texte brut d'un PDF via pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def extract_docx(path: Path) -> str:
    """Extrait le texte brut d'un .docx via python-docx."""
    from docx import Document

    doc = Document(str(path))
    return "\n\n".join(
        para.text for para in doc.paragraphs if para.text.strip()
    )


def extract_text(path: Path) -> str:
    """Lit un fichier texte brut (txt, md)."""
    return path.read_text(encoding="utf-8", errors="replace")


EXTRACTORS: dict[str, Callable[[Path], str]] = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".txt": extract_text,
    ".md": extract_text,
}


# ── Helpers ───────────────────────────────────────────────────────────────────


def slugify(name: str) -> str:
    """Convertit un nom de fichier en slug Obsidian-friendly."""
    base = Path(name).stem
    slug = re.sub(r"[^\w\s-]", "", base.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    return slug or "untitled"


def discover_files(source_dir: Path) -> list[Path]:
    """Trouve tous les fichiers supportés dans un dossier (récursif)."""
    files: list[Path] = []
    for ext in EXTRACTORS:
        files.extend(source_dir.rglob(f"*{ext}"))
    return sorted(files)


def load_env(output_dir: Path) -> None:
    """Charge le .env depuis le vault (parent de inbox/) ou cwd."""
    env_path = output_dir.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # fallback : cherche dans cwd


# ── Fact-Check-Log (piste 6D) ─────────────────────────────────────────────────


def extract_note_title(markdown: str, fallback: str) -> str:
    """Extrait le premier `# Titre` d'un markdown (apres frontmatter).

    Si aucun titre H1 n'est trouve, retourne `fallback` (generalement
    le nom de fichier sans extension).
    """
    # Skip frontmatter si present (--- ... ---)
    body = markdown
    if markdown.lstrip().startswith("---"):
        parts = markdown.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip() or fallback
    return fallback


def append_fact_check_log(
    vault_dir: Path,
    note_title: str,
    source_file: Path,
    source_type: str,
    today: str,
) -> None:
    """Append une entree dans 99-Meta/Fact-Check-Log.md apres traitement d'un fichier.

    No-op si le dossier 99-Meta/ n'existe pas (vault pre-6A ou non configure).
    Piste 6D — traçabilite des sources pour /file-intel.
    """
    log_path = vault_dir / "99-Meta" / "Fact-Check-Log.md"
    if not log_path.exists():
        return
    entry = (
        f"\n## {today} — [[{note_title}]]\n"
        f"- **Source** : {source_type} (`{source_file}`)\n"
        "- **Skill** : /file-intel\n"
        "- **Statut** : to-verify\n"
    )
    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        # Log cassable mais non bloquant pour le traitement lui-meme
        pass


# ── Traitement principal ──────────────────────────────────────────────────────


def process_file(
    file_path: Path,
    output_dir: Path,
    provider: LLMProvider,
) -> Path | None:
    """Traite un fichier : extrait, résume, écrit dans output_dir.

    Returns:
        Path du fichier généré, ou None en cas d'échec.
    """
    extractor = EXTRACTORS.get(file_path.suffix.lower())
    if not extractor:
        print(f"  ⚠ Format non supporté : {file_path.name}", file=sys.stderr)
        return None

    try:
        content = extractor(file_path)
    except Exception as exc:
        print(
            f"  ✗ Échec extraction {file_path.name} : {exc}",
            file=sys.stderr,
        )
        return None

    if not content.strip():
        print(
            f"  ⚠ Fichier vide après extraction : {file_path.name}",
            file=sys.stderr,
        )
        return None

    print(f"  → {provider.__class__.__name__} traite {file_path.name}")
    try:
        markdown = provider.summarize(
            content=content,
            source_filename=file_path.name,
        )
    except Exception as exc:
        print(f"  ✗ Échec LLM {file_path.name} : {exc}", file=sys.stderr)
        return None

    out_path = output_dir / f"{slugify(file_path.name)}.md"
    out_path.write_text(markdown, encoding="utf-8")

    # Piste 6D — trace la source dans 99-Meta/Fact-Check-Log.md (best-effort)
    # output_dir = <vault>/inbox → parent = <vault>
    note_title = extract_note_title(markdown, fallback=out_path.stem)
    source_type = source_type_from_filename(file_path.name)
    append_fact_check_log(
        vault_dir=output_dir.parent,
        note_title=note_title,
        source_file=file_path,
        source_type=source_type,
        today=date.today().isoformat(),
    )

    return out_path


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage : file_intel.py <dossier_source> <dossier_inbox>",
            file=sys.stderr,
        )
        return 2

    source_dir = Path(sys.argv[1]).expanduser().resolve()
    output_dir = Path(sys.argv[2]).expanduser().resolve()

    if not source_dir.is_dir():
        print(
            f"Erreur : {source_dir} n'existe pas ou n'est pas un dossier",
            file=sys.stderr,
        )
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    load_env(output_dir)

    try:
        provider = get_provider()
    except (ValueError, RuntimeError) as exc:
        print(f"Erreur config LLM : {exc}", file=sys.stderr)
        return 1

    files = discover_files(source_dir)
    if not files:
        print(
            f"Aucun fichier supporté trouvé dans {source_dir}",
            file=sys.stderr,
        )
        print(
            f"Extensions supportées : {', '.join(EXTRACTORS.keys())}",
            file=sys.stderr,
        )
        return 1

    print(
        f"Traitement de {len(files)} fichier(s) "
        f"avec {provider.__class__.__name__}..."
    )
    print()

    success = 0
    for file in files:
        if process_file(file, output_dir, provider):
            success += 1

    print()
    print(f"✓ {success}/{len(files)} fichier(s) traité(s) → {output_dir}")
    return 0 if success == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
