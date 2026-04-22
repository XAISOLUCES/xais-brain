"""conftest.py — configuration pytest partagée par tous les tests.

Ajoute `scripts/` au `sys.path` pour que les tests puissent importer
`budget`, `file_intel`, `vault_audit`, `web_clip` directement sans avoir
à dupliquer un `sys.path.insert(...)` en tête de chaque fichier de test.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
