"""Tests unitaires pour file_intel.py."""
import sys
from pathlib import Path

# Ajouter scripts/ au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from file_intel import slugify, discover_files, EXTRACTORS
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
