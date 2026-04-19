# Changelog — Ignorance → Knowledge

All notable changes to this project will be documented in this file.

## [Unreleased] — 2026-04-19

### Added
- **Fact-Checker Bot MVP** — Verifies claims against verified sources only
- Source list: Quran (Arabic), Bukhari, Muslim, UN, WHO, UNRWA, PZoA
- Confidence scoring per source (0.8–1.0)
- Rejection of unverified sources with clear error message
- CLI: `check "<claim>" --source <source_name>`, `sources` (list verified)
- Privacy: No user data stored; only verification log
- Demo script: `demo.py` shows verification workflow
- Tests: `test_verifier.py` (verified claim, unverified source rejection)
- Documentation: README.md with integration examples

### Principles
- **Verification Before Speech:** Only verified sources allowed
- **No Speculation:** Cannot check claim without explicit source citation
- **No fabricated hadith:** Hadith only from Bukhari/Muslim (authentic)
- **Action Before Speech:** Architecture + CLI implemented before public launch

---

**Status: MVP Complete ✅ Ready for integration into agent workflows**
