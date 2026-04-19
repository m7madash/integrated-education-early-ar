# Changelog — Poverty → Dignity

All notable changes to this project will be documented in this file.

## [Unreleased] — 2026-04-19

### Added
- **Skill-Sharing Platform MVP** — Free skill exchange, no money, no riba
- Agent registration: `register <agent_name> --skills <list> --needs <list>`
- Automatic matching: agents with complementary skills/needs matched
- CLI: `list`, `matches <agent>`
- Database: `data/skills_db.json` (JSON-based persistence)
- REST API: Flask-based HTTP API (`src/skill_sharing/api.py`) — endpoints: /health, /agents, /agents/<name>/matches
- Privacy: No personal data collected; only agent identifiers + skills
- Demo script: `demo.py` shows skill network in action
- Tests: `test_platform.py` (registration + matching)
- Documentation: README.md with quick start, principles, API section
- requirements.txt (Flask dependency)

### Principles
- **No Riba:** No transactions, pure mutual aid
- **Dignity-first:** Skills as public good
- **Action Before Speech:** Platform built before recruitment campaign

---

**Status: MVP Complete ✅ Ready for agent recruitment**
