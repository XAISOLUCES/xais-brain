"""Tests pour web_clip.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from web_clip import slugify, ContentExtractor


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
