#!/usr/bin/env python3
"""Sync the catalog into the prompt generator (embedded + standalone JSON)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "serpapi-engine-mcp-catalog.json"
PROMPT_INDEX = ROOT / "prompt-generator" / "index.html"
PROMPT_CATALOG = ROOT / "prompt-generator" / "catalog.json"
DOCS_INDEX = ROOT / "docs" / "index.html"


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text())
    PROMPT_CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")

    payload = json.dumps(catalog, ensure_ascii=False)
    html = PROMPT_INDEX.read_text()
    pattern = r"const catalogPayload = .*?;\n"
    replacement = f"const catalogPayload = {payload};\n"
    updated, count = re.subn(pattern, replacement, html, flags=re.S)
    if count != 1:
        raise SystemExit(f"Expected 1 catalogPayload replacement, got {count}")
    PROMPT_INDEX.write_text(updated)
    DOCS_INDEX.write_text(updated)


if __name__ == "__main__":
    main()
