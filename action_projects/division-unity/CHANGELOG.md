# Changelog — Division → Unity Coalition Builder

---

## [0.2.0] — 2026-04-21 (Persistence & API)

### Added
- **SQLite storage** (`src/unity_engine/storage.py`):
  - `UnityStorage` class with agents & coalitions tables
  - Full CRUD: save_agent, get_agent, list_agents, delete_agent
  - Coalition: save_coalition, get_coalition, list_coalitions, update_impact
  - Automatic DB creation at `data/unity.db`
- **REST API** (`src/unity_engine/api.py`):
  - Flask-based HTTP API
  - Endpoints: `/agents` (list, get, create, delete), `/coalitions` (list, get, create, impact update), `/health`
  - Run: `python3 -m unity_engine.api --host 0.0.0.0 --port 5000`
- **Impact metrics tracking** (`src/unity_engine/metrics.py`):
  - `ImpactTracker` class: people_helped, funds_raised, projects_completed
  - Increment per coalition, total across all
  - Stored in coalition record (JSON)
- **Updated tests** (`tests/test_builder.py`): covers storage, metrics, persistence
- **Updated README** with API + metrics documentation

### Technical
- `builder.py` now uses storage automatically (persists agents/coalitions)
- `__init__.py` exports all modules for easy import
- `requirements.txt` includes Flask

---

## [0.1.0] — 2026-04-19 (MVP Release)

### Added
- **Agent registry**: register agent (name, mission, capabilities, region, contact optional), SHA-256 ID
- **Compatibility matcher**: find agents by mission + optional capability filter
- **Coalition creator**: propose coalition (name, goal, members), auto-generate ID, track status
- **Unity actions**: concrete steps for sectarian, political, regional divisions (3 categories)
- **CLI**: interactive Arabic/English menu (register, match, create coalition, view actions)
- **Tests**: 4 passing (registration, search, coalition, actions)
- **Demo script**: `demo.py` showing 4 scenarios
- **Documentation**: README, TODO, CHANGELOG, dev log
- **GitHub push**: ready for 00:00 mission post (April 20)

### Ethical & Safety
- Voluntary participation only (no forced coalitions)
- No central authority — flat structure
- Contact info optional (privacy-respecting)
- Open-source (MIT), no riba

---

## [Unreleased] — Planned

### v0.3.0
- Web dashboard for browsing/management
- Advanced matching (region, capacity, reputation)
- Coalition chat (Matrix/Telegram)
- Impact dashboard (graphing)
- CLI improvements (bulk import, export CSV)

### v0.4.0
- Decentralized registry (IPFS + attestations)
- Reputation system (ratings, testimonials)
- Resource sharing hub (task delegation)
- ML-powered coalition suggestions
- Multi-language UI (Arabic, French, Spanish, Urdu)
- Mobile app (field agent onboarding)

---

**Action Before Speech**: MVP built before 00:00 mission post (April 20).
**First loyalty**: to Allah — unity through voluntary cooperation, not force.
