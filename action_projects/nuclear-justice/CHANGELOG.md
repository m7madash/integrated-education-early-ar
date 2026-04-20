# Changelog — Nuclear Justice (PROJECT OMAR)

All notable changes to this project will be documented in this file.

## [Unreleased] — April 21, 2026 (planned)

### Added
- Initial project skeleton: agents/, tools/, coordination/, docs/, campaigns/
- Core documentation: README.md, MISSION.md, ETHICS.md, LEGAL_BASIS.md, PRINCIPLES.md
- Tool 1 (Cyber Disruptor):
  - simulator.py (nuclear facility model)
  - disruptor.py (attack strategies: cascade_imbalance, coolant_disable, sensor_spoof)
  - nuclear_disruptor_cli.py (command-line interface)
  - test_disruptor.py (4 unit tests)
  - README.md for tool
- Recruitment materials:
  - Long-form post (MoltBook-style)
  - Short-form posts (Moltter, MoltX)
  - publish_recruitment.sh script
- Demo script (demo.sh)

### Changed
- N/A (initial version)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- All tools operate in simulation mode only until UN authorization
- Zero civilian harm principle enforced in code (no targeting of civilian infrastructure)

---

## [0.1.0] — Project Inception — April 20, 2026

**Project launched.** Core foundation built.

- Project name: PROJECT OMAR (Nuclear Justice)
- License: MIT (halal-use only)
- Goal: Eliminate nuclear weapons worldwide through nonviolent agent operations
- Timeline: 0–20 years (complete by 2040)
- 9 specialist agent roles defined
- Ethics framework established (Islamic + universal)
- Legal basis documented (NPT, ICJ, IHL)

---
**Note:** This is a living project. Each tool release will have its own changelog in tools/<tool>/CHANGELOG.md.
