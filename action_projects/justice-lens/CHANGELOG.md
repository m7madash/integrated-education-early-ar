# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core fairness metrics (statistical parity, equal opportunity, disparate impact)
- Synthetic demo dataset generation
- REST API (FastAPI) with audit endpoint
- CLI for local audits
- Initial test suite

### Changed
- None yet

### Fixed
- None yet

## [0.1.0] — 2026-04-21 (planned)
First public release — Justice Lens bias auditor.

### Added
- Audit engine with 5 fairness metrics
- FastAPI REST API (full CRUD for agents, matches, coalitions)
- SQLite persistence layer (UnityStorage)
- ImpactTracker for coalition metrics
- CLI (interactive Arabic/English menu)
- Demo datasets (synthetic + public)
- Tests (unit + integration)
- Documentation (README, quickstart, deployment guide)
