# Resource Justice — Changelog

All notable changes will be documented here.

## [Unreleased] — 2026-04-21

### Added
- Project inception — Tool 10: War → Peace extension
- `README.md` — full vision, structure, Islamic ethics
- `src/resource_justice/collector.py` — budget data collector (stub)
- `src/resource_justice/calculator.py` — impact calculator (stub)
- `src/resource_justice/api.py` — Flask REST API (stub)
- `src/resource_justice/cli.py` — command-line interface (stub)
- `scripts/collect_data.sh` — runs collector
- `scripts/run_demo.sh` — demo impact scenario
- `scripts/publish_impact.sh` — social media publication script
- `data/budgets.json` — sample military/development budgets (5 countries)
- `data/countries.json` — country metadata (pop, GDP, hunger_rate)
- `data/indicators.json` — cost constants (meal, school, healthcare)
- `requirements.txt` — Flask, requests, python-dotenv

### Planned
- v0.1.0: Basic calculator, CLI, demo, docs
- v0.2.0: Live API integration (SIPRI, World Bank), web dashboard
- v0.3.0: Crowdfunding bridge, smart contracts, OpenClaw skill
