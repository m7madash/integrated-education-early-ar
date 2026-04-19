# Changelog — Pollution → Cleanliness

All notable changes to this project will be documented in this file.

## [Unreleased] — 2026-04-19

### Added
- **Environmental Privacy Monitor MVP** — Air/water quality tracking for Palestine
- Location registration: `add <name> <type:air|water|soil> <lat> <lng>`
- Reading recording: `record <id> <metric> <value> <unit>`
- Air quality summary: `air` (AQI + status: Good/Moderate/Unhealthy/Hazardous)
- Privacy-first design: aggregated data only; no personal identifiers
- Database: `data/environmental_data.json`
- Pre-seeded locations: Gaza City (air), Khan Younis (water)
- Demo script: `demo.py` shows locations, readings, adding new station
- Tests: `test_monitor.py` (add location, record reading, AQI status logic)
- Documentation: README.md (environmental justice focus, Palestine-centric)

### Principles
- **Environmental Justice:** Clean air/water are human rights
- **Privacy Shield Integration:** No individual data; aggregate only
- **Action Before Speech:** Monitoring active before public advocacy

---

**Status: MVP Complete ✅ Ready for field sensor integration**
