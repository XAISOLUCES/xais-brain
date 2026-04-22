"""Tests unitaires pour budget.py (piste 6F — budget annoncé avant batch)."""
import json
from pathlib import Path

# scripts/ est ajouté au sys.path via tests/conftest.py

from budget import (
    BudgetEstimate,
    estimate_batch,
    estimate_file_input_tokens,
    estimate_file_pages,
    format_budget_line,
    load_pricing,
)


# ── load_pricing ──────────────────────────────────────────────────────────────


def test_load_pricing_returns_defaults_when_no_vault():
    pricing = load_pricing(vault_dir=None)
    assert "providers" in pricing
    assert "heuristics" in pricing
    assert "gemini" in pricing["providers"]
    assert pricing["providers"]["gemini"]["input_per_1m_usd"] == 0.0


def test_load_pricing_returns_defaults_when_file_missing(tmp_path):
    pricing = load_pricing(vault_dir=tmp_path)
    assert pricing["providers"]["claude"]["output_per_1m_usd"] == 5.0


def test_load_pricing_reads_user_pricing(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "pricing.json").write_text(
        json.dumps(
            {
                "providers": {
                    "claude": {
                        "model": "test-model",
                        "input_per_1m_usd": 99.0,
                        "output_per_1m_usd": 999.0,
                    }
                },
                "heuristics": {"tokens_per_pdf_page": 1000},
            }
        )
    )
    pricing = load_pricing(vault_dir=tmp_path)
    # user pricing écrase
    assert pricing["providers"]["claude"]["input_per_1m_usd"] == 99.0
    assert pricing["heuristics"]["tokens_per_pdf_page"] == 1000
    # fallback conservé pour les clés manquantes
    assert pricing["providers"]["gemini"]["input_per_1m_usd"] == 0.0
    assert pricing["heuristics"]["output_tokens_per_file"] == 800


def test_load_pricing_fallback_on_corrupted_json(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "pricing.json").write_text("{ this is not valid JSON")
    pricing = load_pricing(vault_dir=tmp_path)
    # doit retomber sur les défauts, sans exception
    assert pricing["providers"]["gemini"]["input_per_1m_usd"] == 0.0


# ── estimate_file_pages ───────────────────────────────────────────────────────


def test_estimate_pages_txt(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("x" * 5000)  # ~5 KB → ~3 pages
    pages = estimate_file_pages(f, {"paragraphs_per_docx_page": 30})
    assert pages >= 1


def test_estimate_pages_md(tmp_path):
    f = tmp_path / "readme.md"
    f.write_text("hello")  # petit fichier → 1 page min
    pages = estimate_file_pages(f, {})
    assert pages == 1


def test_estimate_pages_unknown_extension(tmp_path):
    f = tmp_path / "image.png"
    f.write_bytes(b"\x89PNG...")
    pages = estimate_file_pages(f, {})
    assert pages == 1


def test_estimate_pages_pdf_fallback_on_error(tmp_path):
    # Fichier avec extension .pdf mais contenu invalide → fallback à 1
    f = tmp_path / "broken.pdf"
    f.write_bytes(b"not-a-real-pdf")
    pages = estimate_file_pages(f, {})
    assert pages == 1


# ── estimate_file_input_tokens ────────────────────────────────────────────────


def test_input_tokens_pdf():
    # 3 pages × 750 tokens/page = 2250
    tokens = estimate_file_input_tokens(
        Path("fake.pdf"), pages=3, heuristics={"tokens_per_pdf_page": 750}
    )
    assert tokens == 2250


def test_input_tokens_txt(tmp_path):
    f = tmp_path / "log.txt"
    f.write_text("x" * 2048)  # 2 KB
    tokens = estimate_file_input_tokens(
        f, pages=1, heuristics={"tokens_per_txt_kb": 250}
    )
    # 2 KB × 250 tokens/KB = 500
    assert tokens == 500


# ── estimate_batch ────────────────────────────────────────────────────────────


def test_estimate_batch_empty_files(tmp_path):
    estimate = estimate_batch([], provider="gemini", vault_dir=tmp_path)
    assert estimate.files_count == 0
    assert estimate.pages_count == 0
    assert estimate.input_tokens == 0
    assert estimate.output_tokens == 0
    assert estimate.cost_low_usd == 0.0
    assert estimate.cost_high_usd == 0.0


def test_estimate_batch_gemini_free(tmp_path):
    """Gemini = free tier → coût 0."""
    f1 = tmp_path / "doc.md"
    f1.write_text("hello")
    f2 = tmp_path / "log.txt"
    f2.write_text("x" * 1024)

    estimate = estimate_batch([f1, f2], provider="gemini", vault_dir=tmp_path)
    assert estimate.files_count == 2
    assert estimate.output_tokens == 2 * 800  # 2 fichiers × 800 tokens output
    assert estimate.cost_low_usd == 0.0
    assert estimate.cost_high_usd == 0.0
    assert estimate.is_free_tier is True
    assert estimate.seconds_low == 2 * 3
    assert estimate.seconds_high == 2 * 12


def test_estimate_batch_claude_has_cost(tmp_path):
    """Claude a un tarif → coût > 0."""
    f = tmp_path / "big.md"
    f.write_text("y" * 10_240)  # 10 KB

    estimate = estimate_batch([f], provider="claude", vault_dir=tmp_path)
    assert estimate.files_count == 1
    assert estimate.is_free_tier is False
    # 10 KB × 250 tok/KB = 2500 tokens input
    # Input : 2500 × 1.0 / 1M = 0.0025 $
    # Output : 800 × 5.0 / 1M = 0.004 $
    # Total ≈ 0.0065 $ → cost_high à ±40 %
    assert estimate.cost_high_usd > 0
    assert estimate.cost_high_usd >= estimate.cost_low_usd


def test_estimate_batch_unknown_provider_defaults_to_zero(tmp_path):
    f = tmp_path / "x.md"
    f.write_text("hi")
    estimate = estimate_batch([f], provider="mistral-whatever", vault_dir=tmp_path)
    assert estimate.cost_low_usd == 0.0
    assert estimate.cost_high_usd == 0.0


# ── format_budget_line ────────────────────────────────────────────────────────


def test_format_budget_line_gemini_free():
    estimate = BudgetEstimate(
        files_count=12,
        pages_count=487,
        input_tokens=365_000,
        output_tokens=9_600,
        cost_low_usd=0.0,
        cost_high_usd=0.0,
        seconds_low=36,
        seconds_high=144,
        is_free_tier=True,
    )
    line = format_budget_line(estimate, provider="gemini")
    assert "12 fichier(s)" in line
    assert "487 pages" in line
    assert "gratuit" in line.lower()
    assert "gemini" in line
    assert "36s" in line
    assert "2 min" in line  # 144s → "2 min"


def test_format_budget_line_claude_with_cost():
    estimate = BudgetEstimate(
        files_count=5,
        pages_count=100,
        input_tokens=75_000,
        output_tokens=4_000,
        cost_low_usd=0.05,
        cost_high_usd=0.12,
        seconds_low=15,
        seconds_high=60,
    )
    line = format_budget_line(estimate, provider="claude")
    assert "$0.05" in line
    assert "$0.12" in line
    assert "claude" in line


def test_format_budget_line_under_one_cent():
    estimate = BudgetEstimate(
        files_count=1,
        pages_count=1,
        input_tokens=100,
        output_tokens=100,
        cost_low_usd=0.003,
        cost_high_usd=0.008,
        seconds_low=3,
        seconds_high=12,
    )
    line = format_budget_line(estimate, provider="openai")
    # cost_high < 0.01 → affichage "< $0.01"
    assert "< $0.01" in line
