# Climate Justice — Changelog

All notable changes to this project will be documented.

## [0.1.0] — 2026-04-21 (In Development)

### Added
- **Water Justice module** (`water.py`):
  - `RegionWater` dataclass: consumption, quality, population
  - `WaterJustice` class: scarcity check, injustice score calculation, recommendations
  - Example regions: Gaza, West Bank, Khartoum, Rwanda, Amsterdam, Dhaka
- **Energy Poverty module** (`energy.py`):
  - `RegionEnergy` dataclass: kWh/person/month, access rate, blackout hours, primary source
  - `EnergyPoverty` class: poverty check, injustice score, recommendations
  - Example regions: Gaza, West Bank, Khartoum, Rwanda, New York, Dhaka
- **Climate Displacement module** (`refugees.py`):
  - `DisplacementEvent` dataclass: region, cause, displaced count, severity scoring
  - `ClimateRefugees` class: event tracking, needs assessment, recommendations
  - Example events: Gaza, Sudan, Mekong Delta, Sahel, Morocco, Pakistan, Caribbean
- **Main Detector** (`detector.py`):
  - `ClimateDetector` class: combines water + energy + displacement into overall score
  - Severity labels (CRITICAL, HIGH, MEDIUM, LOW)
  - Merged recommendations from all modules
- **Tests** (`tests/test_detector.py`): covers each module and full detector
- **Requirements** (`requirements.txt`): Flask for future API, pytest for tests
- **README** with problem statement, modules, usage examples, project structure

### Technical Notes
- Pure Python (stdlib only currently)
- Easy to extend with real data sources (UN, World Bank APIs)
- Modular design: each module can be used independently

---

## [Planned] — Future Releases

### [0.2.0] — Accountability & API
- `accountability.py`: carbon emitters database, climate debt calculations
- `api.py`: Flask REST endpoints (/regions, /water, /energy, /refugees, /polluters)
- Real data integration (UN Water Scarcity Atlas, World Bank Energy Access, IDMC)
- Demo script (`scripts/run_demo.sh`) and publishing script

### [0.3.0] — Visualization & Scale
- Web dashboard (Flask + simple HTML) showing region scores on map
- CLI with interactive menu (like division-unity)
- Batch processing: scan list of regions from JSON
- Export reports (PDF, JSON, CSV)

### [1.0.0] — Production Ready
- Docker image for easy deployment
- Scheduled data updates from APIs
- Multi-language support (Arabic, French, Spanish)
- Integration with ACP (agents can query climate justice data as a service)

---

**Ethical**: This tool is for holding polluters accountable and supporting affected communities — never for displacement or gentrification.
