#!/usr/bin/env python3
"""vault_audit — Scanne le vault Obsidian et produit un rapport d'hygiene.

Usage :
    python3 vault_audit.py <vault_path> [--output <path>] [--migrate] [--json]

Detections MVP (piste 6E) :
    - Notes orphelines      : 0 backlinks ET 0 wikilinks sortants
    - Notes anemiques       : < 100 mots (hors frontmatter)
    - Doublons titre exact  : fichiers de meme nom dans differents dossiers
    - Frontmatter incomplet : manque `statut` OU `source_knowledge`
    - Notes to-verify > 30j : statut != verified avec verification_date > 30j
    - Tags incoherents      : variantes de casse (#ai / #AI / #ia)
    - Wikilinks casses      : [[X]] ou X.md n'existe pas

Flags :
    --output <path> : chemin du rapport (defaut: <vault>/99-Meta/Audit-YYYY-MM-DD.md)
    --migrate       : complete les frontmatter manquants (statut: draft, ...)
    --json          : imprime le rapport en JSON sur stdout (pour scripting)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


# ── Config ────────────────────────────────────────────────────────────────────

ANEMIC_THRESHOLD_WORDS = 100
STALE_TO_VERIFY_DAYS = 30
REQUIRED_FRONTMATTER_FIELDS = ("statut", "source_knowledge")

# Dossiers ignores (meta, config, build)
EXCLUDED_DIRS = {
    ".git",
    ".obsidian",
    ".claude",
    ".trash",
    "node_modules",
    "scripts",
    "99-Meta",  # les rapports d'audit eux-memes ne se comptent pas
}


# ── Parsing frontmatter ───────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
TAG_RE = re.compile(r"(?:^|\s)#([A-Za-z0-9_/\-]+)")


@dataclass
class Note:
    """Une note du vault."""
    path: Path
    rel_path: str  # relatif au vault
    title: str     # stem (nom sans extension)
    raw: str
    body: str
    frontmatter: dict[str, Any]
    wikilinks: set[str] = field(default_factory=set)
    tags: set[str] = field(default_factory=set)
    word_count: int = 0


def parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Extrait le frontmatter YAML minimal et retourne (fm, body).

    Parser maison simple : cle: valeur, listes [a, b, c]. Suffit pour MVP.
    """
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw

    fm_text = match.group(1)
    body = raw[match.end():]
    fm: dict[str, Any] = {}

    for line in fm_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        # Liste inline [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            fm[key] = [item.strip().strip('"\'') for item in inner.split(",") if item.strip()]
        else:
            fm[key] = value.strip('"\'')

    return fm, body


def count_words(text: str) -> int:
    """Compte les mots hors code-blocks et frontmatter."""
    # Retire les blocs code pour ne pas gonfler le count
    cleaned = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return len(cleaned.split())


def extract_wikilinks(body: str) -> set[str]:
    """Retourne l'ensemble des cibles de wikilinks (sans ancre/alias)."""
    return {m.group(1).strip() for m in WIKILINK_RE.finditer(body) if m.group(1).strip()}


def extract_tags(raw: str, frontmatter: dict[str, Any]) -> set[str]:
    """Collecte les tags : frontmatter + inline #tag."""
    tags: set[str] = set()
    fm_tags = frontmatter.get("tags")
    if isinstance(fm_tags, list):
        tags.update(str(t).lstrip("#") for t in fm_tags if t)
    elif isinstance(fm_tags, str):
        tags.update(t.strip().lstrip("#") for t in fm_tags.split(",") if t.strip())
    for m in TAG_RE.finditer(raw):
        tags.add(m.group(1))
    return tags


# ── Scan du vault ─────────────────────────────────────────────────────────────


def iter_markdown_files(vault: Path) -> list[Path]:
    """Liste recursive des .md, en excluant EXCLUDED_DIRS."""
    files: list[Path] = []
    for path in vault.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(vault).parts):
            continue
        files.append(path)
    return sorted(files)


def load_note(path: Path, vault: Path) -> Note:
    """Charge une note et parse frontmatter + wikilinks + tags."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(raw)
    return Note(
        path=path,
        rel_path=str(path.relative_to(vault)),
        title=path.stem,
        raw=raw,
        body=body,
        frontmatter=fm,
        wikilinks=extract_wikilinks(body),
        tags=extract_tags(raw, fm),
        word_count=count_words(body),
    )


# ── Detections ────────────────────────────────────────────────────────────────


def detect_orphans(notes: list[Note]) -> list[Note]:
    """Notes sans backlinks ET sans wikilinks sortants."""
    # Index des titres pointes par au moins une autre note
    targeted: set[str] = set()
    for note in notes:
        for link in note.wikilinks:
            targeted.add(link)

    orphans: list[Note] = []
    for note in notes:
        has_backlinks = note.title in targeted
        has_outlinks = len(note.wikilinks) > 0
        if not has_backlinks and not has_outlinks:
            orphans.append(note)
    return orphans


def detect_anemic(notes: list[Note], threshold: int = ANEMIC_THRESHOLD_WORDS) -> list[Note]:
    """Notes < threshold mots."""
    return [n for n in notes if n.word_count < threshold]


def detect_duplicates(notes: list[Note]) -> list[tuple[Note, Note]]:
    """Paires de notes avec le meme title (stem)."""
    by_title: dict[str, list[Note]] = defaultdict(list)
    for note in notes:
        by_title[note.title].append(note)
    pairs: list[tuple[Note, Note]] = []
    for group in by_title.values():
        if len(group) < 2:
            continue
        # Genere toutes les paires (i < j)
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                pairs.append((group[i], group[j]))
    return pairs


def detect_incomplete_frontmatter(notes: list[Note]) -> list[tuple[Note, list[str]]]:
    """Notes dont il manque au moins un champ requis.

    Returns liste de (note, champs_manquants).
    """
    out: list[tuple[Note, list[str]]] = []
    for note in notes:
        missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if not note.frontmatter.get(f)]
        if missing:
            out.append((note, missing))
    return out


def detect_stale_to_verify(notes: list[Note], days: int = STALE_TO_VERIFY_DAYS) -> list[Note]:
    """Notes statut != verified avec verification_date > `days` jours."""
    cutoff = date.today() - timedelta(days=days)
    stale: list[Note] = []
    for note in notes:
        statut = str(note.frontmatter.get("statut", "")).lower()
        if statut == "verified":
            continue
        v_date = note.frontmatter.get("verification_date")
        if not v_date:
            continue
        try:
            parsed = datetime.strptime(str(v_date), "%Y-%m-%d").date()
        except ValueError:
            continue
        if parsed < cutoff:
            stale.append(note)
    return stale


def detect_tag_conflicts(notes: list[Note]) -> list[tuple[str, list[tuple[str, int]]]]:
    """Groupes de tags considered variantes (meme lowercase) mais casse differente.

    Inclut les variantes evidentes (#ai / #AI) mais pas les traductions (#ai / #ia).
    MVP = normalisation lowercase simple.
    """
    # Collecte tag_original -> count, et lower -> set(originals)
    counts: dict[str, int] = defaultdict(int)
    by_lower: dict[str, set[str]] = defaultdict(set)
    for note in notes:
        for tag in note.tags:
            counts[tag] += 1
            by_lower[tag.lower()].add(tag)

    conflicts: list[tuple[str, list[tuple[str, int]]]] = []
    for lower, originals in by_lower.items():
        if len(originals) > 1:
            group = sorted(((t, counts[t]) for t in originals), key=lambda x: -x[1])
            conflicts.append((lower, group))
    return sorted(conflicts, key=lambda x: x[0])


def detect_broken_wikilinks(notes: list[Note]) -> list[tuple[Note, list[str]]]:
    """Wikilinks [[X]] ou X.md n'existe dans aucune note du vault."""
    existing_titles = {n.title for n in notes}
    broken: list[tuple[Note, list[str]]] = []
    for note in notes:
        missing = sorted(link for link in note.wikilinks if link not in existing_titles)
        if missing:
            broken.append((note, missing))
    return broken


# ── Migration (complete frontmatter manquant) ─────────────────────────────────


def migrate_frontmatter(notes: list[Note]) -> int:
    """Complete les frontmatter manquants avec defaults.

    Defaults :
        statut: draft
        source_knowledge: internal
        verification_date: today (seulement si absent ET si on ajoute statut/source_knowledge)

    Ne touche pas aux valeurs existantes. Retourne le nombre de fichiers modifies.
    """
    today_iso = date.today().isoformat()
    modified = 0

    defaults = {
        "statut": "draft",
        "source_knowledge": "internal",
    }

    for note in notes:
        missing = {k: v for k, v in defaults.items() if not note.frontmatter.get(k)}
        if not missing:
            continue

        # Ajout verification_date si absent
        if not note.frontmatter.get("verification_date"):
            missing["verification_date"] = today_iso

        # Construction du nouveau frontmatter
        new_raw = _inject_frontmatter_fields(note.raw, missing)
        if new_raw != note.raw:
            note.path.write_text(new_raw, encoding="utf-8")
            note.raw = new_raw
            note.frontmatter.update(missing)
            modified += 1

    return modified


def _inject_frontmatter_fields(raw: str, new_fields: dict[str, str]) -> str:
    """Ajoute des champs dans le frontmatter existant ou en cree un nouveau.

    Preserve scrupuleusement les champs existants.
    """
    if not new_fields:
        return raw

    match = FRONTMATTER_RE.match(raw)
    injected_lines = [f"{k}: {v}" for k, v in new_fields.items()]

    if match:
        # Ajoute avant le --- fermant
        fm_body = match.group(1).rstrip("\n")
        new_fm = fm_body + "\n" + "\n".join(injected_lines)
        body = raw[match.end():]
        return f"---\n{new_fm}\n---\n{body}" if not body.startswith("\n") else f"---\n{new_fm}\n---{body}"
    else:
        # Cree un frontmatter au-dessus
        new_fm = "\n".join(injected_lines)
        return f"---\n{new_fm}\n---\n\n{raw}"


# ── Rapport ───────────────────────────────────────────────────────────────────


def render_report(
    vault: Path,
    notes: list[Note],
    elapsed: float,
    orphans: list[Note],
    anemic: list[Note],
    duplicates: list[tuple[Note, Note]],
    incomplete: list[tuple[Note, list[str]]],
    stale: list[Note],
    tag_conflicts: list[tuple[str, list[tuple[str, int]]]],
    broken: list[tuple[Note, list[str]]],
) -> str:
    """Genere le rapport Markdown humain-lisible."""
    today = date.today().isoformat()
    lines: list[str] = [
        f"# Vault Audit — {today}",
        "",
        f"**Vault** : {vault}",
        f"**Notes scannees** : {len(notes)}",
        f"**Temps** : {elapsed:.2f}s",
        "",
        "---",
        "",
        f"## Notes orphelines ({len(orphans)})",
        "",
        "> 0 backlinks ET 0 wikilinks sortants.",
        "",
    ]
    if orphans:
        for n in orphans:
            lines.append(f"- [ ] [[{n.rel_path}]] — 0 backlinks, 0 wikilinks sortants")
    else:
        lines.append("_Aucune note orpheline._")
    lines.extend(["", "---", "", f"## Notes anemiques (< {ANEMIC_THRESHOLD_WORDS} mots) ({len(anemic)})", ""])
    if anemic:
        for n in anemic:
            lines.append(f"- [ ] [[{n.rel_path}]] — {n.word_count} mots")
    else:
        lines.append("_Aucune note anemique._")

    lines.extend(["", "---", "", f"## Doublons (titre exact) ({len(duplicates)})", ""])
    if duplicates:
        for a, b in duplicates:
            lines.append(f"- [ ] [[{a.rel_path}]] ≈ [[{b.rel_path}]]")
    else:
        lines.append("_Aucun doublon._")

    lines.extend(["", "---", "", f"## Frontmatter incomplet ({len(incomplete)})", ""])
    if incomplete:
        for n, miss in incomplete:
            missing_str = ", ".join(f"`{m}`" for m in miss)
            lines.append(f"- [ ] [[{n.rel_path}]] — manque {missing_str}")
    else:
        lines.append("_Tous les frontmatter sont complets._")

    lines.extend([
        "",
        "---",
        "",
        f"## Notes `to-verify` depuis > {STALE_TO_VERIFY_DAYS} jours ({len(stale)})",
        "",
    ])
    if stale:
        for n in stale:
            v = n.frontmatter.get("verification_date", "?")
            s = n.frontmatter.get("statut", "?")
            lines.append(f"- [ ] [[{n.rel_path}]] — statut: {s}, verification_date: {v}")
    else:
        lines.append("_Aucune note non verifiee depuis trop longtemps._")

    lines.extend(["", "---", "", f"## Tags incoherents ({len(tag_conflicts)} groupes)", ""])
    if tag_conflicts:
        for lower, variants in tag_conflicts:
            parts = ", ".join(f"`#{t}` ({c} notes)" for t, c in variants)
            lines.append(f"- [ ] {parts} → unifier ?")
    else:
        lines.append("_Aucune incoherence de tag detectee._")

    lines.extend(["", "---", "", f"## Wikilinks casses ({sum(len(m) for _, m in broken)})", ""])
    if broken:
        for n, miss in broken:
            for target in miss:
                lines.append(f"- [ ] [[{n.rel_path}]] → [[{target}]] (cible inexistante)")
    else:
        lines.append("_Aucun wikilink casse._")

    lines.append("")
    return "\n".join(lines)


def build_json_report(
    vault: Path,
    notes: list[Note],
    elapsed: float,
    orphans: list[Note],
    anemic: list[Note],
    duplicates: list[tuple[Note, Note]],
    incomplete: list[tuple[Note, list[str]]],
    stale: list[Note],
    tag_conflicts: list[tuple[str, list[tuple[str, int]]]],
    broken: list[tuple[Note, list[str]]],
) -> dict[str, Any]:
    """Version JSON serialisable du rapport, pour scripting / CI."""
    return {
        "vault": str(vault),
        "date": date.today().isoformat(),
        "notes_scanned": len(notes),
        "elapsed_seconds": round(elapsed, 3),
        "orphans": [n.rel_path for n in orphans],
        "anemic": [{"path": n.rel_path, "words": n.word_count} for n in anemic],
        "duplicates": [[a.rel_path, b.rel_path] for a, b in duplicates],
        "incomplete_frontmatter": [
            {"path": n.rel_path, "missing": miss} for n, miss in incomplete
        ],
        "stale_to_verify": [
            {
                "path": n.rel_path,
                "statut": n.frontmatter.get("statut"),
                "verification_date": n.frontmatter.get("verification_date"),
            }
            for n in stale
        ],
        "tag_conflicts": [
            {"normalized": lower, "variants": [{"tag": t, "count": c} for t, c in vs]}
            for lower, vs in tag_conflicts
        ],
        "broken_wikilinks": [
            {"path": n.rel_path, "targets": miss} for n, miss in broken
        ],
    }


# ── Orchestration ─────────────────────────────────────────────────────────────


def audit(vault: Path, migrate: bool = False) -> dict[str, Any]:
    """Audit complet du vault. Retourne un dict avec les resultats bruts + rapport md.

    Structure de retour :
        {
            "elapsed": float,
            "notes": list[Note],
            "orphans": ..., "anemic": ..., etc.,
            "report_md": str,
            "report_json": dict,
        }
    """
    if not vault.is_dir():
        raise NotADirectoryError(f"Vault introuvable : {vault}")

    start = time.monotonic()
    files = iter_markdown_files(vault)
    notes = [load_note(f, vault) for f in files]

    migrated = 0
    if migrate:
        migrated = migrate_frontmatter(notes)
        # Recharge les frontmatter modifies pour que l'audit reflete l'apres-migration
        # (simplification: on re-parse tout)
        notes = [load_note(f, vault) for f in files]

    orphans = detect_orphans(notes)
    anemic = detect_anemic(notes)
    duplicates = detect_duplicates(notes)
    incomplete = detect_incomplete_frontmatter(notes)
    stale = detect_stale_to_verify(notes)
    tag_conflicts = detect_tag_conflicts(notes)
    broken = detect_broken_wikilinks(notes)

    elapsed = time.monotonic() - start
    report_md = render_report(
        vault, notes, elapsed, orphans, anemic, duplicates,
        incomplete, stale, tag_conflicts, broken,
    )
    report_json = build_json_report(
        vault, notes, elapsed, orphans, anemic, duplicates,
        incomplete, stale, tag_conflicts, broken,
    )
    report_json["migrated"] = migrated

    return {
        "elapsed": elapsed,
        "notes": notes,
        "orphans": orphans,
        "anemic": anemic,
        "duplicates": duplicates,
        "incomplete": incomplete,
        "stale": stale,
        "tag_conflicts": tag_conflicts,
        "broken": broken,
        "report_md": report_md,
        "report_json": report_json,
        "migrated": migrated,
    }


def default_output_path(vault: Path) -> Path:
    """Defaut : <vault>/99-Meta/Audit-YYYY-MM-DD.md."""
    return vault / "99-Meta" / f"Audit-{date.today().isoformat()}.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vault_audit",
        description="Audit d'hygiene d'un vault Obsidian xais-brain.",
    )
    parser.add_argument("vault", type=str, help="Chemin du vault")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Chemin du rapport Markdown (defaut: <vault>/99-Meta/Audit-YYYY-MM-DD.md)",
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Complete les frontmatter manquants avec les valeurs par defaut",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime le rapport en JSON sur stdout au lieu du Markdown",
    )
    args = parser.parse_args(argv)

    vault = Path(args.vault).expanduser().resolve()

    try:
        result = audit(vault, migrate=args.migrate)
    except NotADirectoryError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result["report_json"], indent=2, ensure_ascii=False))
        return 0

    output_path = Path(args.output).expanduser().resolve() if args.output else default_output_path(vault)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result["report_md"], encoding="utf-8")

    notes_count = len(result["notes"])
    issues = (
        len(result["orphans"])
        + len(result["anemic"])
        + len(result["duplicates"])
        + len(result["incomplete"])
        + len(result["stale"])
        + len(result["tag_conflicts"])
        + sum(len(m) for _, m in result["broken"])
    )

    print(f"Audit termine : {notes_count} notes scannees, {issues} points d'attention.")
    print(f"Rapport : {output_path}")
    if args.migrate:
        print(f"Migration : {result['migrated']} fichier(s) complete(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
