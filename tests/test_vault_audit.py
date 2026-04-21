"""Tests unitaires pour vault_audit.py (piste 6E).

6-8 fixtures couvrant chaque detection : orphelines, anemiques, doublons,
frontmatter incomplet, stale to-verify, tags incoherents, wikilinks casses.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from vault_audit import (
    audit,
    parse_frontmatter,
    count_words,
    extract_wikilinks,
    extract_tags,
    detect_orphans,
    detect_anemic,
    detect_duplicates,
    detect_incomplete_frontmatter,
    detect_stale_to_verify,
    detect_tag_conflicts,
    detect_broken_wikilinks,
    migrate_frontmatter,
    load_note,
    iter_markdown_files,
    main,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def write_note(vault: Path, rel_path: str, content: str) -> Path:
    """Ecrit une note dans le vault (cree les dossiers au besoin)."""
    p = vault / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ── Parsing helpers ───────────────────────────────────────────────────────────


def test_parse_frontmatter_simple():
    fm, body = parse_frontmatter("---\nstatut: draft\ntags: [a, b]\n---\nhello")
    assert fm == {"statut": "draft", "tags": ["a", "b"]}
    assert body.strip() == "hello"


def test_parse_frontmatter_missing():
    fm, body = parse_frontmatter("pas de frontmatter ici")
    assert fm == {}
    assert "pas de frontmatter" in body


def test_count_words_skips_code():
    text = "Un deux trois ```python\nun deux trois quatre cinq\n``` quatre"
    # hors code: "Un deux trois  quatre" -> 4
    assert count_words(text) == 4


def test_extract_wikilinks_basic():
    body = "Voir [[FooBar]] et [[Autre Note]] et [[note#ancre]]."
    links = extract_wikilinks(body)
    assert "FooBar" in links
    assert "Autre Note" in links
    assert "note" in links


def test_extract_tags_inline_and_frontmatter():
    raw = "---\ntags: [alpha, beta]\n---\nHello #gamma et #AI"
    fm = {"tags": ["alpha", "beta"]}
    tags = extract_tags(raw, fm)
    assert {"alpha", "beta", "gamma", "AI"} <= tags


# ── Fixtures builder ──────────────────────────────────────────────────────────


def _build_vault(tmp_path: Path) -> Path:
    """Construit un vault de test avec des cas couvrant chaque detection."""
    vault = tmp_path / "vault"

    # 1) Note orpheline : pas de wikilinks sortants, personne ne la pointe
    write_note(vault, "inbox/orpheline.md", """---
statut: draft
source_knowledge: internal
---

# Orpheline

Je suis seule et personne ne m'aime, mais je contiens assez de mots pour
passer le seuil anémique. Lorem ipsum dolor sit amet consectetur adipiscing
elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit.
""")

    # 2) Note anemique (<100 mots)
    write_note(vault, "daily/2026-01-01.md", """---
statut: draft
source_knowledge: internal
---

# Un jour

Juste quelques mots. Pas assez.
""")

    # 3) Doublons : meme titre dans 2 dossiers
    write_note(vault, "inbox/article.md", """---
statut: draft
source_knowledge: web-checked
---
# Article

Premiere version dans inbox, contient assez de mots pour ne pas etre anemique.
Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua minim veniam quis nostrud exercitation
ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in.
""")
    write_note(vault, "research/article.md", """---
statut: verified
source_knowledge: web-checked
---
# Article

Deuxieme version dans research, elle aussi suffisamment longue pour ne pas etre
anemique du tout. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua minim veniam quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
""")

    # 4) Frontmatter incomplet (manque statut et source_knowledge)
    write_note(vault, "research/incomplete.md", """---
tags: [foo]
---
# Incomplete

Cette note n'a ni statut ni source_knowledge, elle devrait apparaitre dans le
rapport. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua minim veniam quis nostrud
exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute.
""")

    # 5) Note to-verify depuis > 30j
    old_date = (date.today() - timedelta(days=60)).isoformat()
    write_note(vault, "research/stale.md", f"""---
statut: to-verify
source_knowledge: web-checked
verification_date: {old_date}
---
# Stale

Cette note traine depuis 60 jours sans verification. Lorem ipsum dolor sit
amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua minim veniam quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit.
""")

    # 6) Tags incoherents (#ai vs #AI)
    write_note(vault, "research/tagged-low.md", """---
statut: draft
source_knowledge: internal
tags: [ai]
---
# Tagged low

Contenu avec tag ai minuscule pour test incoherence. Lorem ipsum dolor sit
amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua minim veniam quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit.
""")
    write_note(vault, "research/tagged-up.md", """---
statut: draft
source_knowledge: internal
tags: [AI]
---
# Tagged up

Contenu avec tag AI majuscule pour test incoherence. Lorem ipsum dolor sit
amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua minim veniam quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit.
""")

    # 7) Wikilink casse
    write_note(vault, "research/links.md", """---
statut: draft
source_knowledge: internal
---
# Links

Voir [[note-inexistante]] et [[Article]] pour plus de details. Lorem ipsum dolor
sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua minim veniam quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit.
""")

    return vault


# ── Tests de detection individuels ────────────────────────────────────────────


def test_iter_markdown_files_excludes_meta(tmp_path: Path):
    vault = tmp_path / "vault"
    write_note(vault, "inbox/note.md", "hello")
    write_note(vault, "99-Meta/Audit.md", "meta")
    write_note(vault, ".obsidian/workspace.md", "config")
    write_note(vault, "scripts/test.md", "script")

    files = iter_markdown_files(vault)
    rels = [f.relative_to(vault).as_posix() for f in files]
    assert "inbox/note.md" in rels
    assert not any("99-Meta" in r for r in rels)
    assert not any(".obsidian" in r for r in rels)
    assert not any("scripts" in r for r in rels)


def test_audit_finds_orphan(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    orphan_paths = [n.rel_path for n in result["orphans"]]
    assert any("orpheline.md" in p for p in orphan_paths)


def test_audit_finds_anemic(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    anemic_paths = [n.rel_path for n in result["anemic"]]
    assert any("2026-01-01.md" in p for p in anemic_paths)


def test_audit_finds_duplicates(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    # Paire article dans inbox/ et research/
    pairs = [(a.rel_path, b.rel_path) for a, b in result["duplicates"]]
    flat = [p for pair in pairs for p in pair]
    assert any("inbox/article.md" in p for p in flat)
    assert any("research/article.md" in p for p in flat)


def test_audit_finds_incomplete_frontmatter(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    # Recupere les paths des notes flagguees
    paths = [n.rel_path for n, _ in result["incomplete"]]
    assert any("research/incomplete.md" in p for p in paths)
    # Et les champs manquants contiennent statut ou source_knowledge
    for n, missing in result["incomplete"]:
        if "research/incomplete.md" in n.rel_path:
            assert "statut" in missing
            assert "source_knowledge" in missing


def test_audit_finds_stale(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    paths = [n.rel_path for n in result["stale"]]
    assert any("stale.md" in p for p in paths)


def test_audit_finds_tag_conflicts(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    # Il doit y avoir un conflit sur le groupe "ai"
    normalized = [lower for lower, _ in result["tag_conflicts"]]
    assert "ai" in normalized


def test_audit_finds_broken_wikilinks(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    broken_targets = set()
    for note, missing in result["broken"]:
        broken_targets.update(missing)
    assert "note-inexistante" in broken_targets


def test_audit_report_markdown_structure(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    md = result["report_md"]
    # Le rapport doit contenir les 7 sections prevues au plan
    assert "# Vault Audit" in md
    assert "## Notes orphelines" in md
    assert "## Notes anemiques" in md
    assert "## Doublons" in md
    assert "## Frontmatter incomplet" in md
    assert "## Notes `to-verify` depuis > 30 jours" in md
    assert "## Tags incoherents" in md
    assert "## Wikilinks casses" in md


def test_audit_report_json_structure(tmp_path: Path):
    vault = _build_vault(tmp_path)
    result = audit(vault)
    rj = result["report_json"]
    # Keys attendus
    for key in (
        "vault", "date", "notes_scanned", "orphans", "anemic",
        "duplicates", "incomplete_frontmatter", "stale_to_verify",
        "tag_conflicts", "broken_wikilinks",
    ):
        assert key in rj
    # Et serialisation JSON propre
    s = json.dumps(rj, default=str)
    assert "vault" in s


# ── Migration ────────────────────────────────────────────────────────────────


def test_migrate_completes_missing_fields(tmp_path: Path):
    vault = tmp_path / "vault"
    p = write_note(vault, "note.md", """---
tags: [foo]
---
# Note

Body here, au moins quelques mots pour etre valide. Lorem ipsum.
""")

    result = audit(vault, migrate=True)
    # Au moins 1 fichier modifie
    assert result["migrated"] >= 1

    new_raw = p.read_text(encoding="utf-8")
    assert "statut: draft" in new_raw
    assert "source_knowledge: internal" in new_raw
    assert "verification_date:" in new_raw
    # Et le tag existant est preserve
    assert "tags: [foo]" in new_raw


def test_migrate_does_not_overwrite_existing(tmp_path: Path):
    vault = tmp_path / "vault"
    p = write_note(vault, "note.md", """---
statut: verified
source_knowledge: web-checked
---
# Note

Body.
""")
    result = audit(vault, migrate=True)
    assert result["migrated"] == 0
    new_raw = p.read_text(encoding="utf-8")
    assert "statut: verified" in new_raw
    assert "source_knowledge: web-checked" in new_raw


# ── CLI end-to-end ────────────────────────────────────────────────────────────


def test_main_creates_report(tmp_path: Path, capsys):
    vault = _build_vault(tmp_path)
    rc = main([str(vault)])
    assert rc == 0
    # Rapport dans 99-Meta/ cree
    report = vault / "99-Meta" / f"Audit-{date.today().isoformat()}.md"
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "# Vault Audit" in content


def test_main_json_output(tmp_path: Path, capsys):
    vault = _build_vault(tmp_path)
    rc = main([str(vault), "--json"])
    assert rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["vault"] == str(vault)
    assert data["notes_scanned"] > 0


def test_main_nonexistent_vault(tmp_path: Path):
    missing = tmp_path / "nonexistent"
    rc = main([str(missing)])
    assert rc == 1


def test_main_custom_output(tmp_path: Path):
    vault = _build_vault(tmp_path)
    out = tmp_path / "custom-report.md"
    rc = main([str(vault), "--output", str(out)])
    assert rc == 0
    assert out.exists()


def test_main_migrate_flag(tmp_path: Path):
    vault = tmp_path / "vault"
    p = write_note(vault, "note.md", """---
tags: [x]
---
# N

Body content.
""")
    rc = main([str(vault), "--migrate"])
    assert rc == 0
    new_raw = p.read_text(encoding="utf-8")
    assert "statut: draft" in new_raw
