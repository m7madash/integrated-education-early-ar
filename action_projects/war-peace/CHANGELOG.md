# War → Peace — Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — Development Snapshot (Apr 19, 2026)

### Added
- **Core tracker module** (`src/war_peace/tracker.py`):
  - `Conflict` dataclass: tracks conflict zones (location, parties, status, violations)
  - `Ceasefire` dataclass: records agreements (mediators, terms, verification)
  - `CeasefireTracker` class: manages conflicts & ceasefires, calculates metrics
- **CLI** (`src/war_peace/cli.py`): demo runner for terminal
- **Tests** (`tests/test_tracker.py`): 4 tests all passing
  - add_conflict
  - add_ceasefire_and_check
  - broken_ceasefire_detection
  - metrics_calculation
- **Project infrastructure**:
  - README updated with MVP description and usage
  - TODO.md with detailed roadmap (design: 100%, impl: 40%, testing: 100%)
  - Dev log (`logs/dev_2026-04-19.txt`) documenting today's progress
  - `__init__.py` for package import

### Technical Details
- Pure Python, zero external dependencies (uses only standard library)
- Shared utils integration (logging via SummaryLogger)
- Caching design (SimpleCache available, decorator pending)
- Batch file read optimization (ready for data feeds)
- Git-managed, open-source (MIT)

### Demo Output
```
📊 Metrics:
   total_conflicts: 2
   active_ceasefires: 1
   broken_ceasefire: 0
   peace_rate: 50.0%

🔍 Gaza: ceasefire since 2024-01-20, violations: 3 → peace_holding: ❌
🔍 Ukraine: active (since 2022-02-24)
```

### Principles Applied
- **M1 (Justice):** Track wars impartially, count civilian harm
- **M5 (Oppressed):** Highlight ceasefire violations against vulnerable populations
- **Action Before Speech:** Code built **before** any publication

---

## [0.1.0] — Project Init (Apr 18, 2026)

### Added
- Initial project scaffolding (README, TODO draft, CHANGELOG template)
- `publish_war-peace_results.sh` script
- Symlink to shared utils

---

🚀 **GitHub:** https://github.com/m7madash/Abduallh-projects/tree/main/action_projects/war-peace
