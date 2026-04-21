# Riba Danger — Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-04-21 (Initial Release)

### Added
- **Core analyzer** (`analyze.py`): detects riba in loan structures
- **Calculator module** (`calculator.py`):
  - `RibaCalculator` class: APR, effective interest, loan classification
  - `analyze_loan()`: returns verdict + metrics
- **Islamic alternatives** (`halal_alternatives.py`):
  - `Murabaha` (cost-plus financing)
  - `Ijarah` (leasing with ownership transfer)
  - `Musharaka` (partnership buyout)
  - `compare_loan_vs_halal()` — side-by-side cost & halal-status comparison
- **CLI** (`cli.py`): unified interface (interactive, single-shot, batch)
- **Tests** (`tests/test_analyzer.py`): math verification for all models
- **Documentation**: full README with Arabic/English, usage examples, project structure

### Technical Notes
- Pure Python (no external deps beyond stdlib)
- Works offline (no API calls needed)
- Suitable for integration into other agent tools

---

## [Planned] — Future Releases

### [0.2.0] — Enhanced UX
- Web form (HTML+JS) for non-technical users
- Mobile app skeleton (Flutter)
- Arabic video guide (10 min)
- PDF guide: "الربا في المعاملات الحديثة"

### [0.3.0] — Advanced Detection
- Smart contract analysis (DeFi lending protocols)
- Bank statement parser (CSV/MT940)
- Real-world loan database (sample scenarios)

### [1.0.0] — Production
- REST API (FastAPI) for third-party integration
- Browser extension (detect riba on loan websites)
- WhatsApp/Telegram bot for quick checks
- Excel/Google Sheets plugin

---

**Ethical**: Halal-only models. No riba promotion. Transparent math.  
**Urgency**: High — protect Muslim communities from interest-based traps.
