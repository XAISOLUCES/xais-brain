"""Tests unitaires pour file_intel.py."""
import sys
from pathlib import Path

# Ajouter scripts/ au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from file_intel import (
    EXTRACTORS,
    _is_ci_mode,
    announce_budget,
    append_fact_check_log,
    discover_files,
    extract_note_title,
    prompt_checkpoint,
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


# ── Piste 6F : budget annoncé avant batch ─────────────────────────────────────


def test_announce_budget_prints_estimate(tmp_path, capsys, monkeypatch):
    """announce_budget() affiche une estimation lisible avant traitement."""
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    f1 = tmp_path / "a.md"
    f1.write_text("hello")
    f2 = tmp_path / "b.md"
    f2.write_text("world")

    announce_budget([f1, f2], vault_dir=tmp_path)

    captured = capsys.readouterr().out
    assert "2 fichier(s)" in captured
    assert "gemini" in captured
    # Free tier → "gratuit"
    assert "gratuit" in captured.lower()


def test_announce_budget_never_raises_on_bad_files(tmp_path, capsys, monkeypatch):
    """announce_budget() est non-bloquant : aucune exception ne remonte."""
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    # Fichier PDF bidon qui fera planter pypdf
    bad = tmp_path / "broken.pdf"
    bad.write_bytes(b"not-a-pdf")

    # Doit ne pas lever
    announce_budget([bad], vault_dir=tmp_path)


# ── Piste 6C : checkpoints humains ────────────────────────────────────────────


def test_is_ci_mode_xais_brain_ci(monkeypatch):
    """XAIS_BRAIN_CI=1 → mode CI activé."""
    monkeypatch.setenv("XAIS_BRAIN_CI", "1")
    monkeypatch.delenv("CI", raising=False)
    assert _is_ci_mode() is True


def test_is_ci_mode_ci_env(monkeypatch):
    """CI=1 (GitHub Actions) → mode CI activé."""
    monkeypatch.delenv("XAIS_BRAIN_CI", raising=False)
    monkeypatch.setenv("CI", "true")
    assert _is_ci_mode() is True


def test_is_ci_mode_off(monkeypatch):
    """Aucune variable définie → mode CI désactivé."""
    monkeypatch.delenv("XAIS_BRAIN_CI", raising=False)
    monkeypatch.delenv("CI", raising=False)
    assert _is_ci_mode() is False


def test_is_ci_mode_explicit_zero(monkeypatch):
    """XAIS_BRAIN_CI=0 → mode CI désactivé (valeur explicitement falsy)."""
    monkeypatch.setenv("XAIS_BRAIN_CI", "0")
    monkeypatch.delenv("CI", raising=False)
    assert _is_ci_mode() is False


def test_prompt_checkpoint_ci_returns_default_yes(monkeypatch, capsys):
    """En mode CI, le prompt retourne default_yes sans attendre stdin."""
    monkeypatch.setenv("XAIS_BRAIN_CI", "1")
    assert prompt_checkpoint("Go ?", default_yes=True) is True
    out = capsys.readouterr().out
    assert "CI" in out


def test_prompt_checkpoint_ci_returns_default_no(monkeypatch, capsys):
    """En mode CI avec default_yes=False, retourne False sans attendre."""
    monkeypatch.setenv("XAIS_BRAIN_CI", "1")
    assert prompt_checkpoint("Go ?", default_yes=False) is False


def test_prompt_checkpoint_non_tty_returns_default(monkeypatch, capsys):
    """Sans TTY (stdin non interactif), retourne default_yes sans bloquer."""
    monkeypatch.delenv("XAIS_BRAIN_CI", raising=False)
    monkeypatch.delenv("CI", raising=False)
    # stdin n'est pas un TTY dans pytest → isatty() retourne False
    assert prompt_checkpoint("Go ?", default_yes=True) is True
    assert prompt_checkpoint("Go ?", default_yes=False) is False


def test_prompt_checkpoint_stdin_yes(monkeypatch, capsys):
    """Une réponse 'oui' stdin retourne True."""
    monkeypatch.delenv("XAIS_BRAIN_CI", raising=False)
    monkeypatch.delenv("CI", raising=False)
    # Simule un TTY avec une réponse prête
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "oui")
    assert prompt_checkpoint("Go ?", default_yes=False) is True


def test_prompt_checkpoint_stdin_no(monkeypatch, capsys):
    """Une réponse 'non' stdin retourne False même si default=True."""
    monkeypatch.delenv("XAIS_BRAIN_CI", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "non")
    assert prompt_checkpoint("Go ?", default_yes=True) is False


def test_prompt_checkpoint_stdin_empty_uses_default(monkeypatch, capsys):
    """Une réponse vide (juste Entrée) retourne default_yes."""
    monkeypatch.delenv("XAIS_BRAIN_CI", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "")
    assert prompt_checkpoint("Go ?", default_yes=True) is True
    assert prompt_checkpoint("Go ?", default_yes=False) is False


def test_prompt_checkpoint_stdin_eof_returns_false(monkeypatch, capsys):
    """Un EOF (Ctrl+D) retourne False (user a coupé net → safe to abort)."""
    monkeypatch.delenv("XAIS_BRAIN_CI", raising=False)
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    def _raise_eof():
        raise EOFError()

    monkeypatch.setattr("builtins.input", _raise_eof)
    assert prompt_checkpoint("Go ?", default_yes=True) is False


def test_announce_budget_reads_user_pricing_json(tmp_path, capsys, monkeypatch):
    """announce_budget() lit `.claude/pricing.json` du vault si présent."""
    monkeypatch.setenv("LLM_PROVIDER", "claude")
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    # Pricing custom : Claude facturé 100 $/M tokens → coût non nul
    import json as _json

    (claude_dir / "pricing.json").write_text(
        _json.dumps(
            {
                "providers": {
                    "claude": {
                        "model": "claude-haiku",
                        "input_per_1m_usd": 100.0,
                        "output_per_1m_usd": 500.0,
                    }
                }
            }
        )
    )
    f = tmp_path / "big.md"
    f.write_text("x" * 4096)

    announce_budget([f], vault_dir=tmp_path)

    captured = capsys.readouterr().out
    assert "claude" in captured
    # Coût > 0 → doit apparaître dans la ligne ($ visible)
    assert "$" in captured
