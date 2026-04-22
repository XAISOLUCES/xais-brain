"""Tests unitaires pour file_intel.py."""
import sys
from pathlib import Path

# Ajouter scripts/ au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from file_intel import (
    EXTRACTORS,
    append_fact_check_log,
    discover_files,
    extract_note_title,
    slugify,
)
from providers._prompts import (
    build_summarization_prompt,
    source_type_from_filename,
)


def test_slugify_normal():
    assert slugify("Mon Document.pdf") == "mon-document"


def test_slugify_special_chars():
    assert slugify("rapport_Q1 (2026).docx") == "rapport_q1-2026"


def test_slugify_empty():
    assert slugify("") == "untitled"


def test_slugify_accents():
    assert slugify("resume-etude.txt") == "resume-etude"


def test_extractors_keys():
    assert set(EXTRACTORS.keys()) == {".pdf", ".docx", ".txt", ".md"}


def test_discover_files_empty(tmp_path):
    assert discover_files(tmp_path) == []


def test_discover_files_mixed(tmp_path):
    (tmp_path / "doc.pdf").touch()
    (tmp_path / "notes.md").touch()
    (tmp_path / "image.png").touch()  # pas supporté
    files = discover_files(tmp_path)
    assert len(files) == 2
    names = {f.name for f in files}
    assert names == {"doc.pdf", "notes.md"}


# ── Piste 6B : frontmatter enrichi via le prompt LLM ──────────────────────────


def test_source_type_pdf():
    assert source_type_from_filename("rapport.pdf") == "pdf"


def test_source_type_docx():
    assert source_type_from_filename("note.DOCX") == "docx"


def test_source_type_txt():
    assert source_type_from_filename("log.txt") == "txt"


def test_source_type_md():
    assert source_type_from_filename("README.md") == "md"


def test_source_type_unknown_fallback():
    assert source_type_from_filename("truc.xyz") == "import"


def test_prompt_contains_enriched_frontmatter_pdf():
    """Le prompt doit instruire le LLM de produire un frontmatter piste 6B."""
    prompt = build_summarization_prompt(
        content="Lorem ipsum", source_filename="rapport-annuel.pdf"
    )
    assert "source: pdf" in prompt
    assert "source_file: rapport-annuel.pdf" in prompt
    assert "source_knowledge: internal" in prompt
    assert "verification_date:" in prompt
    assert "statut: to-verify" in prompt
    assert "importance: medium" in prompt


def test_prompt_contains_enriched_frontmatter_docx():
    prompt = build_summarization_prompt(
        content="Hello", source_filename="notes.docx"
    )
    assert "source: docx" in prompt
    assert "source_file: notes.docx" in prompt


def test_prompt_preserves_instructions_no_modify():
    """Le prompt doit explicitement interdire au LLM de modifier les metadata."""
    prompt = build_summarization_prompt(
        content="x", source_filename="a.pdf"
    )
    # Le LLM ne doit pas renommer / modifier les champs
    assert "Ne modifie PAS les valeurs de `source`" in prompt or "recopie-les" in prompt


# ── Piste 6D : Fact-Check-Log auto-alimenté ───────────────────────────────────


def test_extract_note_title_with_frontmatter():
    """Extrait le H1 apres un frontmatter YAML."""
    md = """---
source: pdf
statut: to-verify
---

# Mon Titre

Contenu ici.
"""
    assert extract_note_title(md, fallback="fallback") == "Mon Titre"


def test_extract_note_title_no_frontmatter():
    """Extrait le H1 sans frontmatter."""
    md = "# Autre Titre\n\nContenu."
    assert extract_note_title(md, fallback="fallback") == "Autre Titre"


def test_extract_note_title_fallback_when_no_h1():
    """Retourne le fallback si aucun H1."""
    md = "## Pas de H1\n\nContenu."
    assert extract_note_title(md, fallback="mon-fichier") == "mon-fichier"


def test_extract_note_title_ignores_h2():
    """Ne confond pas un H2 avec un H1."""
    md = "---\nx: y\n---\n\n## Section\n\n# Vrai Titre\n"
    assert extract_note_title(md, fallback="fb") == "Vrai Titre"


def test_append_fact_check_log_appends_when_file_exists(tmp_path):
    """Si 99-Meta/Fact-Check-Log.md existe, une entree file-intel est appendee."""
    meta_dir = tmp_path / "99-Meta"
    meta_dir.mkdir()
    log = meta_dir / "Fact-Check-Log.md"
    log.write_text("# Fact-Check Log\n\n---\n", encoding="utf-8")

    source = Path("./docs/rapport.pdf")
    append_fact_check_log(
        vault_dir=tmp_path,
        note_title="Rapport Annuel",
        source_file=source,
        source_type="pdf",
        today="2026-04-22",
    )

    content = log.read_text(encoding="utf-8")
    assert "## 2026-04-22 — [[Rapport Annuel]]" in content
    assert "pdf" in content
    assert "rapport.pdf" in content
    assert "/file-intel" in content
    assert "to-verify" in content


def test_append_fact_check_log_noop_when_file_missing(tmp_path):
    """Si 99-Meta/Fact-Check-Log.md n'existe pas, pas d'erreur (vault pre-6A)."""
    append_fact_check_log(
        vault_dir=tmp_path,
        note_title="Test",
        source_file=Path("./foo.docx"),
        source_type="docx",
        today="2026-04-22",
    )
    assert not (tmp_path / "99-Meta").exists()


def test_append_fact_check_log_multiple_entries_append_only(tmp_path):
    """Plusieurs appels ajoutent plusieurs entrees (append-only)."""
    meta_dir = tmp_path / "99-Meta"
    meta_dir.mkdir()
    log = meta_dir / "Fact-Check-Log.md"
    log.write_text("# Fact-Check Log\n\n---\n", encoding="utf-8")

    append_fact_check_log(
        tmp_path, "Note A", Path("a.pdf"), "pdf", "2026-04-22"
    )
    append_fact_check_log(
        tmp_path, "Note B", Path("b.docx"), "docx", "2026-04-22"
    )

    content = log.read_text(encoding="utf-8")
    assert "[[Note A]]" in content
    assert "[[Note B]]" in content
    # L'ordre est preserve : A avant B
    assert content.index("Note A") < content.index("Note B")
