"""budget.py — Estimation de budget (tokens, temps, coût) pour les skills batch.

Piste 6F — xais-brain god-mode patterns.

Lit `.claude/pricing.json` à la racine du vault. Si absent, retombe sur des
valeurs par défaut hardcodées (conservatrices) pour ne jamais planter.

Usage :
    from budget import estimate_batch, format_budget_line
    estimate = estimate_batch(files, provider="gemini", vault_dir=vault_path)
    print(format_budget_line(estimate, provider="gemini"))
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# ── Valeurs par défaut (fallback si .claude/pricing.json introuvable) ─────────

_DEFAULT_PRICING: dict = {
    "providers": {
        "gemini": {
            "model": "gemini-2.0-flash",
            "input_per_1m_usd": 0.0,
            "output_per_1m_usd": 0.0,
        },
        "claude": {
            "model": "claude-haiku-4-5-20251001",
            "input_per_1m_usd": 1.0,
            "output_per_1m_usd": 5.0,
        },
        "openai": {
            "model": "gpt-4o-mini",
            "input_per_1m_usd": 0.15,
            "output_per_1m_usd": 0.60,
        },
    },
    "heuristics": {
        "tokens_per_pdf_page": 750,
        "paragraphs_per_docx_page": 30,
        "tokens_per_txt_kb": 250,
        "output_tokens_per_file": 800,
        "seconds_per_file_min": 3,
        "seconds_per_file_max": 12,
    },
}


# ── API publique ──────────────────────────────────────────────────────────────


@dataclass
class BudgetEstimate:
    """Estimation d'un batch de fichiers à traiter."""

    files_count: int
    pages_count: int  # total de pages (PDF) + équivalent (DOCX/TXT)
    input_tokens: int
    output_tokens: int
    cost_low_usd: float
    cost_high_usd: float
    seconds_low: int
    seconds_high: int
    is_free_tier: bool = False  # True si le provider a un tarif à 0 (gemini free)


def load_pricing(vault_dir: Path | None = None) -> dict:
    """Charge `.claude/pricing.json` depuis le vault, fallback sur les défauts.

    Si ``vault_dir`` est None, retourne directement les valeurs par défaut.
    Si le fichier est illisible (JSON cassé, permission), fallback silencieux.
    """
    if vault_dir is None:
        return _DEFAULT_PRICING

    pricing_path = vault_dir / ".claude" / "pricing.json"
    if not pricing_path.exists():
        return _DEFAULT_PRICING

    try:
        with pricing_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return _DEFAULT_PRICING

    # Merge additif : si une clé manque dans le JSON user, on retombe sur
    # les valeurs par défaut (robuste aux pricing.json partiels).
    merged: dict = {
        "providers": {**_DEFAULT_PRICING["providers"], **data.get("providers", {})},
        "heuristics": {**_DEFAULT_PRICING["heuristics"], **data.get("heuristics", {})},
    }
    return merged


def estimate_file_pages(file_path: Path, heuristics: dict) -> int:
    """Estime le nombre de pages équivalentes d'un fichier.

    PDF : vrai nombre de pages via pypdf.
    DOCX : len(paragraphes) / paragraphs_per_docx_page.
    TXT/MD : taille / 2048 octets (heuristique grossière).
    Autre : 1 page par défaut.

    En cas d'erreur d'extraction, retourne 1 (conservateur).
    """
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            from pypdf import PdfReader

            return max(1, len(PdfReader(str(file_path)).pages))
        if suffix == ".docx":
            from docx import Document

            doc = Document(str(file_path))
            paragraphs = [p for p in doc.paragraphs if p.text.strip()]
            per_page = heuristics.get("paragraphs_per_docx_page", 30) or 30
            return max(1, len(paragraphs) // per_page + 1)
        if suffix in {".txt", ".md"}:
            size = file_path.stat().st_size
            return max(1, size // 2048 + 1)
    except Exception:
        return 1
    return 1


def estimate_file_input_tokens(file_path: Path, pages: int, heuristics: dict) -> int:
    """Estime les tokens d'entrée pour un fichier selon son type."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return pages * heuristics.get("tokens_per_pdf_page", 750)
    if suffix == ".docx":
        # 1 page DOCX ≈ 1 page PDF en densité de tokens : on réutilise le même
        # ratio que PDF pour éviter la sous-estimation de ~40 % constatée
        # précédemment avec la formule `pages * per_page * per_para // 10`.
        return pages * heuristics.get("tokens_per_pdf_page", 750)
    if suffix in {".txt", ".md"}:
        try:
            size_kb = max(1, file_path.stat().st_size // 1024)
        except OSError:
            size_kb = 1
        return size_kb * heuristics.get("tokens_per_txt_kb", 250)
    # fallback
    return pages * heuristics.get("tokens_per_pdf_page", 750)


def estimate_batch(
    files: Iterable[Path],
    provider: str,
    vault_dir: Path | None = None,
) -> BudgetEstimate:
    """Calcule une estimation de budget pour un batch de fichiers.

    Args:
        files: itérable de Path vers les fichiers à traiter.
        provider: 'gemini' | 'claude' | 'openai' (ou autre → tarif 0).
        vault_dir: racine du vault pour lire `.claude/pricing.json`. Optionnel.

    Returns:
        BudgetEstimate (nb fichiers, pages, tokens, coût, temps).
    """
    pricing = load_pricing(vault_dir)
    heuristics = pricing["heuristics"]
    providers = pricing["providers"]
    prov_cfg = providers.get(provider, {})

    files_list = list(files)
    files_count = len(files_list)

    pages_total = 0
    input_tokens_total = 0
    for f in files_list:
        pages = estimate_file_pages(f, heuristics)
        pages_total += pages
        input_tokens_total += estimate_file_input_tokens(f, pages, heuristics)

    output_per_file = heuristics.get("output_tokens_per_file", 800)
    output_tokens_total = files_count * output_per_file

    input_rate = float(prov_cfg.get("input_per_1m_usd", 0.0))
    output_rate = float(prov_cfg.get("output_per_1m_usd", 0.0))
    is_free_tier = input_rate == 0.0 and output_rate == 0.0

    cost_mid = (
        input_tokens_total * input_rate / 1_000_000
        + output_tokens_total * output_rate / 1_000_000
    )
    # fourchette ±40 % pour refléter l'incertitude de l'estimation
    cost_low = round(cost_mid * 0.6, 2)
    cost_high = round(cost_mid * 1.4, 2)

    sec_min = heuristics.get("seconds_per_file_min", 3)
    sec_max = heuristics.get("seconds_per_file_max", 12)
    seconds_low = files_count * sec_min
    seconds_high = files_count * sec_max

    return BudgetEstimate(
        files_count=files_count,
        pages_count=pages_total,
        input_tokens=input_tokens_total,
        output_tokens=output_tokens_total,
        cost_low_usd=cost_low,
        cost_high_usd=cost_high,
        seconds_low=seconds_low,
        seconds_high=seconds_high,
        is_free_tier=is_free_tier,
    )


def _format_seconds(seconds: int) -> str:
    """Format humain : '45s', '3 min', '12 min'."""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    return f"{minutes} min"


def _format_cost(cost_low: float, cost_high: float, is_free_tier: bool = False) -> str:
    """Format humain du coût : 'gratuit', '~$0.05', '$0.50-$1.20'."""
    if is_free_tier:
        return "gratuit (free tier)"
    if cost_high < 0.01:
        return "< $0.01"
    if cost_low == cost_high:
        return f"~${cost_low:.2f}"
    return f"${cost_low:.2f}-${cost_high:.2f}"


def format_budget_line(estimate: BudgetEstimate, provider: str) -> str:
    """Retourne le bloc de 2 lignes affiché avant exécution d'un batch.

    Exemple :
        /file-intel va traiter 12 fichier(s) (~487 pages).
        Estimation : 36s-2 min, gratuit (free tier) (provider: gemini).
    """
    time_str = (
        f"{_format_seconds(estimate.seconds_low)}-{_format_seconds(estimate.seconds_high)}"
    )
    cost_str = _format_cost(
        estimate.cost_low_usd, estimate.cost_high_usd, is_free_tier=estimate.is_free_tier
    )
    header = (
        f"/file-intel va traiter {estimate.files_count} fichier(s) "
        f"(~{estimate.pages_count} pages)."
    )
    detail = f"Estimation : {time_str}, {cost_str} (provider: {provider})."
    return f"{header}\n{detail}"
