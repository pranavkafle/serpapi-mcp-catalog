# SerpApi MCP Engine Catalog

A curated, engine-by-engine catalog for the official SerpApi MCP server. This repo distills the SerpApi docs into a consistent JSON shape so agents and apps can generate strong system prompts and avoid parameter mistakes.

## What's inside

- `data/serpapi-engine-mcp-catalog.json` — primary catalog (engine metadata, params, descriptions, examples).
- `prompt-generator/` — standalone HTML generator with an embedded catalog.
- `reports/` — test artifacts from MCP runs (for reference only).
- `scripts/` — helper scripts for scraping and syncing.
- `assets/` — screenshots used in documentation.

## Quick start

Open the prompt generator directly:

```
open prompt-generator/index.html
```

Pick an engine, copy the generated prompt, and paste it into your bot/agent system prompt.

![Prompt generator preview](assets/ui.png)

## Notes

- The official docs sometimes mark `k` as optional for search engines, but MCP calls fail without `k` or an equivalent query parameter. To reduce runtime errors, `k` is treated as required in this catalog.
- The catalog is meant to be practical for MCP usage, even when the docs are incomplete or inconsistent.

## Sync the prompt generator

If you edit the catalog, re-embed it into the generator:

```
python scripts/sync-catalog.py
```

## License

See the repository root `LICENSE`.
