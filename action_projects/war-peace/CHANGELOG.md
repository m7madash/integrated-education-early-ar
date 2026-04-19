# Changelog — War → Peace

All notable changes to this project will be documented in this file.

## [Unreleased] — 2026-04-19

### Added
- **Ceasefire Tracker MVP** — Monitor active conflicts, violations, casualties
- Conflict registration: `add <name> <location> <parties>`
- Real-time updates: `update <id> <casualties> <violations>`
- Gaza-specific summary: `gaza` command (24h metrics + ceasefire status)
- Data source integration (mock): UN OCHA placeholder for real API
- Database: `data/conflicts.json` (JSON persistence)
- Privacy: Aggregated counts only; no individual victim names stored (respect for dignity)
- Demo script: `demo.py` shows tracking + update workflow
- Tests: `test_tracker.py` (add conflict, update violations, get summary)
- Documentation: README.md with data sources roadmap (OCHA, ACLED, MoH)

### Principles
- **Every Victim Counts:** Casualty count drives urgency; count = 0 target
- **Stand with Oppressed:** Focus on Palestine (Gaza) primary
- **Action Before Speech:** Tracker built, data collection started before advocacy

---

**Status: MVP Complete ✅ Data integration pending (OCHA API, ACLED feed)**
