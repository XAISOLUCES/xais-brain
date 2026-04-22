"""Tests pour web_clip.py."""
from datetime import date
from pathlib import Path

# scripts/ est ajouté au sys.path via tests/conftest.py

from web_clip import (
    ContentExtractor,
    _is_safe_url,
    append_fact_check_log,
    build_frontmatter,
    slugify,
)


def test_slugify():
    assert slugify("Mon Article - Le Monde") == "mon-article-le-monde"


def test_slugify_long():
    long_title = "A" * 200
    assert len(slugify(long_title)) <= 80


def test_extractor_basic():
    html = "<html><title>Test</title><body><p>Hello world</p></body></html>"
    ext = ContentExtractor()
    ext.feed(html)
    assert ext.title == "Test"
    assert "Hello world" in ext.get_markdown()


def test_extractor_skips_nav():
    html = "<nav>Menu</nav><p>Content</p><footer>Footer</footer>"
    ext = ContentExtractor()
    ext.feed(html)
    md = ext.get_markdown()
    assert "Content" in md
    assert "Menu" not in md
    assert "Footer" not in md


def test_extractor_headings():
    html = "<h2>Titre</h2><p>Texte</p>"
    ext = ContentExtractor()
    ext.feed(html)
    md = ext.get_markdown()
    assert "## Titre" in md


# ── Piste 6B : frontmatter enrichi ────────────────────────────────────────────


def test_frontmatter_enriched_contains_required_fields():
    """Le frontmatter clip doit contenir les champs piste 6B."""
    url = "https://example.com/article"
    today = date.today().isoformat()
    fm = build_frontmatter(url, today)

    # Nouveaux champs piste 6B
    assert "source: web" in fm
    assert f"source_url: {url}" in fm
    assert "source_knowledge: web-checked" in fm
    assert f"verification_date: {today}" in fm
    assert "statut: draft" in fm
    assert "importance: medium" in fm

    # Champs historiques preserves
    assert "type: web-clip" in fm
    assert f"clipped: {today}" in fm
    assert "tags: [inbox, web]" in fm

    # Delimiteurs YAML
    assert fm.startswith("---\n")
    assert fm.endswith("---")


def test_frontmatter_source_url_not_renamed_from_source():
    """Verifie que l'URL n'est PAS dans `source:` (nouveau schema). L'URL va dans `source_url:`."""
    url = "https://foo.bar/path"
    fm = build_frontmatter(url, "2026-04-21")
    # source: web (pas l'URL elle-meme)
    assert "source: web" in fm
    # Et l'URL est bien dans source_url
    assert "source_url: https://foo.bar/path" in fm


def test_append_fact_check_log_appends_when_file_exists(tmp_path):
    """Si 99-Meta/Fact-Check-Log.md existe, une entree est appendee."""
    meta_dir = tmp_path / "99-Meta"
    meta_dir.mkdir()
    log = meta_dir / "Fact-Check-Log.md"
    log.write_text("# Fact-Check Log\n\n---\n", encoding="utf-8")

    append_fact_check_log(tmp_path, "Mon Article", "https://example.com/x", "2026-04-21")

    content = log.read_text(encoding="utf-8")
    assert "## 2026-04-21 — [[Mon Article]]" in content
    assert "https://example.com/x" in content
    assert "/clip" in content
    assert "draft" in content


def test_append_fact_check_log_noop_when_file_missing(tmp_path):
    """Si le fichier n'existe pas, pas d'erreur (vault pre-6A)."""
    # Aucun 99-Meta/ cree
    append_fact_check_log(tmp_path, "Test", "https://x.y", "2026-04-21")
    assert not (tmp_path / "99-Meta").exists()


# ── SSRF (is_safe_url) ────────────────────────────────────────────────────────


def test_is_safe_url_rejects_file_scheme():
    """Un scheme file:// doit être refusé (SSRF classique)."""
    assert _is_safe_url("file:///etc/passwd") is False


def test_is_safe_url_rejects_non_http_schemes():
    """Schemes exotiques (gopher, ftp, data) refusés."""
    assert _is_safe_url("gopher://example.com") is False
    assert _is_safe_url("ftp://example.com") is False
    assert _is_safe_url("data:text/plain,hello") is False


def test_is_safe_url_rejects_loopback():
    """127.0.0.1 et localhost doivent être refusés."""
    assert _is_safe_url("http://127.0.0.1/admin") is False
    # localhost peut résoudre vers ::1 ou 127.0.0.1 — les deux sont rejetés
    assert _is_safe_url("http://localhost:8080/api") is False


def test_is_safe_url_accepts_public_https():
    """Un domaine public en https doit être accepté."""
    # example.com est un domaine réservé IANA pour la doc, toujours public
    assert _is_safe_url("https://example.com/") is True


def test_is_safe_url_rejects_missing_hostname():
    """Une URL sans hostname valide est refusée."""
    assert _is_safe_url("http:///no-host") is False
    assert _is_safe_url("not-a-url") is False
