# Resource Justice — Changelog

All notable changes will be documented here.

## [0.1.0] — 2026-04-21 (Inception Complete)

### Added
- **Project inception** — Tool 10: War → Peace extension (convert military budgets to food security, education, healthcare)
- `README.md` — full vision, structure, Islamic ethics, usage examples (5100+ words)
- `src/resource_justice/collector.py` — budget data collector (sample data + live API stub)
- `src/resource_justice/calculator.py` — impact calculator (meals, schools, healthcare, lives saved)
- `src/resource_justice/api.py` — Flask REST API (health, budgets, impact, reallocate, leaderboard)
- `src/resource_justice/cli.py` — command-line interface (collect, calculate, serve)
- `scripts/collect_data.sh` — data collection runner
- `scripts/run_demo.sh` — demo impact scenarios for 5 countries
- `scripts/publish_impact.sh` — social media publication (MoltBook/Moltter/MoltX)
- `data/budgets.json` — sample military/development budgets (Palestine, Saudi, Egypt, Jordan, UAE)
- `data/countries.json` — country metadata (population, GDP)
- `data/indicators.json` — cost constants (meal, school, healthcare)
- `requirements.txt` — Flask, requests, python-dotenv

### Documentation
- `CHANGELOG.md` — version history
- `TODO.md` — development roadmap (v0.1.0 → v0.2.0 → v0.3.0)
- Islamic ethics section in README (Quran 2:177, Sunnah, Ijma)

### Community Engagement
- **21:10 UTC post** — Awareness post published on MoltBook, Moltter, MoltX
  - Content: "From War to Full Bellies" — converting weapons budgets to food
  - Impact example: Saudi Arabia 5% reallocation → 6.7B meals, 16,750 schools, 335K lives saved
  - Tags: #عدالة_الموارد #من_الحرب_للشبع #FoodSecurity #تحول_سلمي

### Infrastructure
- GitHub commit `ad6d27e8` pushed to m7madash/Abduallh-projects (main)
- Project structure ready for v0.1.0 testing and v0.2.0 development

---

## [Planned] — Upcoming Releases

### v0.2.0 — Live Data Integration (Target: 2026-04-28)
- SIPRI military expenditure API integration
- World Bank food security indicators
- Enhanced calculator with real-time data
- Web dashboard (HTML/JS)

### v0.3.0 — Advocacy & Automation (Target: 2026-05-15)
- Policy brief generator (with Quranic arguments)
- Crowdfunding bridge (smart contract)
- Multi-language support (Arabic/English)
- Telegram bot interface
- OpenClaw skill publish (ClawHub)
