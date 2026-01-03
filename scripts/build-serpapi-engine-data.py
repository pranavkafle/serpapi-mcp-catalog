#!/usr/bin/env python3
"""Build SerpApi engine parameter data for MCP usage."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

RAW_JSON_EXPORT = False
PLAYGROUND_URL = "https://serpapi.com/playground"
OUT_DIR = Path("docs/data/engines-raw" if RAW_JSON_EXPORT else "docs/data/engines-normalized")
ENGINE_INDEX_PATH = Path("docs/data/engine-index.json")
EXCLUDED_ENGINES = {"google_scholar_profiles", "google_light_fast"}

PARAM_KEEP_KEYS = {"html", "type", "options", "required"}


def _is_numeric(value: object) -> bool:
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        return value.isdigit()
    return False


def normalize_options(options: list) -> list:
    normalized = []
    for option in options:
        if isinstance(option, list) and option:
            value = option[0]
            label = option[1] if len(option) > 1 else None
            if label is not None and _is_numeric(value) and value != label:
                normalized.append(option)
            else:
                normalized.append(value)
        else:
            normalized.append(option)
    return normalized


class _HtmlToMarkdown(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.in_code = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            self.parts.append("\n")
            return
        if tag == "code":
            self.in_code = True
            self.parts.append("`")
            return
        if tag == "a":
            return

    def handle_endtag(self, tag: str) -> None:
        if tag == "code":
            if self.in_code:
                self.parts.append("`")
                self.in_code = False
            return
        if tag == "a":
            return

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_markdown(self) -> str:
        text = "".join(self.parts)
        return " ".join(text.split())


def html_to_markdown(value: str) -> str:
    parser = _HtmlToMarkdown()
    parser.feed(html.unescape(value))
    return parser.get_markdown()


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_props(page_html: str) -> dict:
    match = re.search(r'data-react-props="([^"]+)"', page_html)
    if not match:
        raise RuntimeError("Failed to locate data-react-props in playground HTML.")
    raw = html.unescape(match.group(1))
    return json.loads(raw)


def normalize_engine(engine: str, payload: dict) -> dict:
    if RAW_JSON_EXPORT:
        return {
            "engine": engine,
            "source": PLAYGROUND_URL,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

    normalized_params: dict[str, dict[str, object]] = {}
    common_params: dict[str, dict[str, object]] = {}
    if isinstance(payload, dict):
        for group_name, group in payload.items():
            if not isinstance(group, dict):
                continue
            params = group.get("parameters")
            if not isinstance(params, dict):
                continue
            for param_name, param in params.items():
                if not isinstance(param, dict):
                    continue
                filtered = {k: v for k, v in param.items() if k in PARAM_KEEP_KEYS}
                options = filtered.get("options")
                if isinstance(options, list):
                    filtered["options"] = normalize_options(options)
                html_value = filtered.pop("html", None)
                if isinstance(html_value, str):
                    filtered["description"] = html_to_markdown(html_value)
                if filtered:
                    filtered["group"] = group_name
                    if group_name == "serpapi_parameters":
                        common_params[param_name] = filtered
                    else:
                        normalized_params[param_name] = filtered

    return {"engine": engine, "params": normalized_params, "common_params": common_params}


def main() -> int:
    html_text = fetch(PLAYGROUND_URL)
    props = extract_props(html_text)
    params = props.get("parameters")
    if not isinstance(params, dict):
        raise RuntimeError("Playground props missing 'parameters' map.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    engines = []

    for engine, payload in sorted(params.items()):
        if not isinstance(engine, str):
            continue
        if engine in EXCLUDED_ENGINES:
            continue
        normalized = normalize_engine(engine, payload)
        out_path = OUT_DIR / f"{engine}.json"
        out_path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
        count += 1
        engines.append(engine)

    ENGINE_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENGINE_INDEX_PATH.write_text(json.dumps({"engines": engines}, indent=2), encoding="utf-8")

    label = "raw" if RAW_JSON_EXPORT else "normalized"
    print(f"Wrote {count} {label} engine files to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
