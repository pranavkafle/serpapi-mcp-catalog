# SerpApi MCP Engine Catalog

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-live-brightgreen)](https://pranavkafle.github.io/serpapi-mcp-catalog/)
[![License](https://img.shields.io/github/license/pranavkafle/serpapi-mcp-catalog)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/pranavkafle/serpapi-mcp-catalog)](https://github.com/pranavkafle/serpapi-mcp-catalog/commits/main)

A curated, engine-by-engine catalog for the official SerpApi MCP server. This repo distills the SerpApi docs into a consistent JSON shape so agents and apps can generate strong system prompts and avoid parameter mistakes.

Live demo: https://pranavkafle.github.io/serpapi-mcp-catalog/

## What's inside

- `data/serpapi-engine-mcp-catalog.json` — primary catalog (engine metadata, params, descriptions, examples).
- `prompt-generator/` — standalone HTML generator with an embedded catalog.
- `docs/` — GitHub Pages site (same generator).
- `reports/` — test artifacts from MCP runs (for reference only).
- `scripts/` — helper scripts for scraping and syncing.
- `assets/` — screenshots used in documentation.

## Quick start

Open the prompt generator locally:

```
open prompt-generator/index.html
```

Pick an engine, copy the generated prompt, and paste it into your bot/agent system prompt.

![Prompt generator preview](assets/ui.png)

## Notes

- The official docs sometimes mark `k` as optional for search engines, but MCP calls fail without `k` or an equivalent query parameter. To reduce runtime errors, `k` is treated as required in this catalog.
- The catalog is meant to be practical for MCP usage, even when the docs are incomplete or inconsistent.

## Sync the prompt generator

If you edit the catalog, re-embed it into the generator and GitHub Pages copy:

```
python scripts/sync-catalog.py
```

## License

Apache-2.0. See `LICENSE`.
