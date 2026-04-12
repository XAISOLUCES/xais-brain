"""Tests unitaires pour file_intel.py."""
import sys
from pathlib import Path

# Ajouter scripts/ au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from file_intel import slugify, discover_files, EXTRACTORS


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
