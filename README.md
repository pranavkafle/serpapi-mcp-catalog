# SerpApi MCP Engine Catalog

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-live-brightgreen)](https://pranavkafle.github.io/serpapi-mcp-catalog/)
[![License](https://img.shields.io/github/license/pranavkafle/serpapi-mcp-catalog)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/pranavkafle/serpapi-mcp-catalog)](https://github.com/pranavkafle/serpapi-mcp-catalog/commits/main)

A curated, engine-by-engine parameter catalog for the official SerpApi MCP server. This repo builds a consistent JSON shape from SerpApi's playground data so agents and apps can generate strong system prompts and avoid parameter mistakes.

Live demo: https://pranavkafle.github.io/serpapi-mcp-catalog/

## What's inside

- `docs/` — GitHub Pages site (prompt generator + data).
- `docs/data/engines-normalized/` — per-engine JSON data for the generator.
- `docs/data/engine-index.json` — list of engines for the generator.
- `scripts/` — data build script.
- `assets/` — screenshots used in documentation.

## Quick start

Build data and open the prompt generator locally:

```
python scripts/build-serpapi-engine-data.py
python -m http.server 8000
```

Then open `http://localhost:8000/docs/index.html`, pick an engine, copy the generated prompt, and paste it into your bot/agent system prompt.

![Prompt generator preview](assets/ui.png)

## Notes

- The catalog is meant to be practical for MCP usage, even when the docs are incomplete or inconsistent.

## License

Apache-2.0. See `LICENSE`.
