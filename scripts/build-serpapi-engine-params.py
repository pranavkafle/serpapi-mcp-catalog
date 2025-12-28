#!/usr/bin/env python3
"""Build SerpApi engine + parameter map from official docs."""

from __future__ import annotations

import concurrent.futures
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BASE_URL = "https://serpapi.com"
INDEX_PATH = "/search-engine-apis"
OUT_PARAMS_PATH = "data/serpapi-engine-params.json"
OUT_ENGINES_PATH = "data/serpapi-engines.json"
EXTRA_PATHS = [
    "/bing-product-api",
]


class ParamParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_section = False
        self.in_param_item = False
        self.param_item_depth = 0
        self.current_field: str | None = None
        self.current: dict[str, str] | None = None
        self.items: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k: v for k, v in attrs if v is not None}
        if tag == "section" and attrs_dict.get("id") == "parameters":
            self.in_section = True
            return
        if not self.in_section:
            return
        if tag == "div" and "class" in attrs_dict and "param-item" in attrs_dict["class"]:
            self.in_param_item = True
            self.param_item_depth = 1
            self.current = {"name": "", "required": "", "description": ""}
            self.current_field = None
            return
        if self.in_param_item and tag == "div":
            self.param_item_depth += 1
        if self.in_param_item and tag == "p":
            cls = attrs_dict.get("class", "")
            if "param-name" in cls:
                self.current_field = "name"
            elif "param-req" in cls:
                self.current_field = "required"
            elif "param-des" in cls:
                self.current_field = "description"

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.in_section:
            self.in_section = False
            return
        if not self.in_section:
            return
        if self.in_param_item and tag == "div":
            self.param_item_depth -= 1
            if self.param_item_depth == 0 and self.current:
                name = " ".join(self.current["name"].split()).strip()
                description = " ".join(self.current["description"].split()).strip()
                req_text = " ".join(self.current["required"].split()).strip()
                required: bool | None = None
                if req_text:
                    required = req_text.lower().startswith("required")
                if name:
                    self.items.append(
                        {
                            "name": name,
                            "required": required,
                            "description": description,
                        }
                    )
                self.in_param_item = False
                self.current = None
                self.current_field = None
            return
        if self.in_param_item and tag == "p":
            self.current_field = None

    def handle_data(self, data: str) -> None:
        if not (self.in_param_item and self.current_field and self.current):
            return
        self.current[self.current_field] += data


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def slug_to_engine(slug: str) -> str | None:
    slug = slug.strip("/")
    if not slug:
        return None
    if slug == "search-api":
        return "google"
    if slug.endswith("-search-api"):
        base = slug[: -len("-search-api")]
        return base.replace("-", "_")
    if slug.endswith("-api"):
        slug = slug[: -len("-api")]
    return slug.replace("-", "_")


def extract_doc_paths(index_html: str) -> list[str]:
    index_html = html.unescape(index_html)
    exclude_prefixes = (
        "/users/",
        "/pricing",
        "/integrations",
        "/use-cases",
        "/team",
        "/careers",
        "/faq",
        "/legal",
        "/security",
        "/blog",
        "/#",
        "/contact",
        "/api-status-and-error-codes",
    )
    paths: set[str] = set()
    for match in re.finditer(r'href="(/[^"#]+)"', index_html):
        href = match.group(1)
        if href in ("/", INDEX_PATH):
            continue
        if any(href.startswith(prefix) for prefix in exclude_prefixes):
            continue
        paths.add(href.rstrip("/"))
    return sorted(paths)




def extract_params(page_html: str) -> list[dict[str, object]]:
    parser = ParamParser()
    parser.feed(page_html)
    return parser.items


def extract_engines_from_page(page_html: str) -> set[str]:
    engines = set()
    for pat in (
        r"engine=([a-z0-9_]+)",
        r"\"engine\"\s*:\s*\"([a-z0-9_]+)\"",
        r"engine\s*[:=]\s*\"?([a-z0-9_]+)\"?",
    ):
        for match in re.finditer(pat, page_html, re.I):
            engines.add(match.group(1).lower())
    return engines


def build_engine_map(paths: list[str]) -> dict[str, dict[str, object]]:
    engine_map: dict[str, dict[str, object]] = {}

    def fetch_page(path: str) -> tuple[str, str]:
        return path, fetch(urljoin(BASE_URL, path))

    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        futures = [executor.submit(fetch_page, path) for path in paths]
        for future in concurrent.futures.as_completed(futures):
            path, page_html = future.result()
            slug = path.strip("/").split("/")[-1]
            engine = slug_to_engine(slug)
            if not engine:
                continue
            engines_in_page = extract_engines_from_page(page_html)
            if engine not in engines_in_page:
                continue
            params = extract_params(page_html)
            existing = engine_map.get(engine)
            if existing and len(existing.get("params", [])) >= len(params):
                continue
            engine_map[engine] = {
                "doc_url": urljoin(BASE_URL, path),
                "params": params,
            }

    return engine_map


def main() -> int:
    index_html = fetch(urljoin(BASE_URL, INDEX_PATH))
    seed_paths = extract_doc_paths(index_html)
    paths = sorted(set(seed_paths).union(EXTRA_PATHS))

    engine_map = build_engine_map(paths)
    engines = sorted(engine_map.keys())

    for engine in engines:
        params = engine_map[engine].get("params", [])
        required = [p["name"] for p in params if p.get("required") is True]
        optional = [p["name"] for p in params if p.get("required") is False]
        engine_map[engine]["required_params"] = required
        engine_map[engine]["optional_params"] = optional

    payload = {
        "source": f"{BASE_URL}{INDEX_PATH}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_count": len(engines),
        "engines": engine_map,
    }

    with open(OUT_PARAMS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    engines_payload = {
        "source": f"{BASE_URL}{INDEX_PATH}",
        "count": len(engines),
        "engines": engines,
    }
    with open(OUT_ENGINES_PATH, "w", encoding="utf-8") as f:
        json.dump(engines_payload, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PARAMS_PATH} with {len(engines)} engines")
    print(f"Wrote {OUT_ENGINES_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
