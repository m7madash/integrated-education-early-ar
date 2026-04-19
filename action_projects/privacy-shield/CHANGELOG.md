# Privacy Shield — Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased] — Development (Apr 19, 2026)

### Added
- **CLI prototype** (`src/privacy_shield/cli.py`):
  - `--encrypt-file` / `--decrypt-file` demo (XOR cipher)
  - `--check-breach` demo (simulated, HIBP integration pending)
  - `--harden-browser` (Firefox presets: resist fingerprinting, DoH)
  - `--vpn-status` (IP disclosure check)
- **Demo script** (`demo.py`) — standalone, zero dependencies
  - File encryption/decryption round-trip verified
  - Breach check demo (mock response)
  - Browser hardening presets listing
- **Project infrastructure**:
  - README expanded to full mission + problem statement (Webloc verified by Citizen Lab)
  - TODO.md with phased roadmap (Phase 1–5)
  - Existing tools: `simple_rtb_blocker.py` (RTB/webloc blocking)
  - Existing docs: `guide/`, `advocacy/`, `education/` folders

### Technical Notes
- Pure Python stdlib for demo (no external packages)
- XOR cipher used for demo only — **NOT for production**
- Production crypto will use `cryptography` (Fernet/AES-256)
- Breach check uses HaveIBeenPwned API (v3) — rate-limited, key optional
- Browser hardening targets Firefox first (Chrome later)

### Principles Applied
- **M1 (Justice):** Surveillance is oppression — tools fight back
- **M4 (No Harm):** Prevent data harvesting that leads to harm
- **M5 (Stand with Oppressed):** Palestinians, immigrants, protesters targeted by Webloc
- **Action Before Speech:** CLI built before any public announcement

---

## [0.1.0] — Project Init (Apr 18, 2026)

### Added
- Initial project scaffolding:
  - README with Webloc/ Cobwebs Technologies overview
  - TODO draft (manual tasks)
  - CHANGELOG template
  - `tools/simple_rtb_blocker.py` (early ad-blocker guide)
  - Directories: `advocacy/`, `education/`, `guide/`, `logs/`

### Notes
Project originated from need to protect Palestinian activists from Webloc location tracking by ICE/Israel-affiliated data brokers.

---

🚀 **GitHub:** https://github.com/m7madash/Abduallh-projects/tree/main/action_projects/privacy-shield
