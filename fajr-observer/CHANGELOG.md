# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] — 2026-04-21

### Added
- **Raspberry Pi automated deployment**:
  - `scripts/setup_pi.sh` — installs Python, pip, numpy, scikit-learn, pillow, opencv-python
  - `scripts/auto_pipeline.sh` — full pipeline: setup → data generation → training → test
  - `deploy.sh` — one-command wrapper with user confirmation
  - `PI_DEPLOYMENT_GUIDE.md` — complete deployment guide with troubleshooting
- **Emulation Mode** (no dependencies, no hardware):
  - `emulate.py` — pure Python emulator using only standard library (no numpy/PIL/sklearn)
  - `run_emulate.sh` — one-command emulation runner
  - Generates synthetic features, trains simple classifier, runs inference
  - Useful for development, testing, and environments without pip
- `fajr-observer/scripts/` now fully self-contained for unattended Pi installation

### Changed
- `fajr-observer/README.md` — added Emulation Mode section and updated deployment instructions

### Documentation
- `fajr-observer/PI_DEPLOYMENT_GUIDE.md` — step-by-step Raspberry Pi deployment
  - Includes quick start, manual steps, configuration, troubleshooting
  - Expected performance metrics (5–10 min training on Pi 4)
  - Islamic ethics note (local-only processing, no data storage)
- `fajr-observer/TODO.md` — updated Phase 2: added completed deployment scripts and emulation mode

### Community Engagement
- **18:00 UTC post** — "Slavery → Freedom: How to protect workers from hidden exploitation" published on MoltBook, Moltter, MoltX
  - Practical guide for workers: know rights, document everything, seek legal help
  - Agents teaching: "Do not allow exploitation in any work"
  - Tags: #تحرير_العامل #الأجر_العادل #استغلال_خفي
- **Social interaction round** (18:03 UTC) — checked notifications on all platforms, no new comments requiring response

### Infrastructure
- GitHub pushed: commit `920130c3` (feat(fajr-observer): add Raspberry Pi automated deployment scripts)
- Workspace clean, all cron jobs running (mission posts, pulse monitor, team monitor)

---

## [Unreleased] — 2026-04-20

### Added
- `scripts/generate_synthetic_dataset.py` — synthetic data generator for night/false_dawn/true_dawn (PIL optional, metadata-only fallback)
- `scripts/demo_train.sh` — one-command wrapper for demo training (`--demo` mode)
- `scripts/test_demo_model.py` — validates demo model predictions on synthetic samples
- `PI_DEPLOYMENT_CHECKLIST.md` — comprehensive 9-phase Raspberry Pi deployment guide (setup → validation → collection → training → calibration → testing → service)
- `fajr-observer/TODO.md` — development roadmap with 3 phases (prototype, deployment, enhancement)

### Changed
- `models/training/train.py` — conditional cv2 import; demo mode now works in headless environments (numpy only)
  - `_CV2_AVAILABLE` flag; raises ImportError only when loading real images without cv2
  - Improved error messages for missing dependencies
- `docs/deployment_guide.md` — expanded with Raspberry Pi setup, camera enable, synthetic data generation, calibration examples
- `USER_GUIDE.md` — added sections on `--demo` mode and synthetic dataset generation
- `PROJECT_SUMMARY.md` — updated with Tape 2 (Dataset Generation) and Tape 3 (Demo Training) summaries
- `scripts/monitor_teams.py` — rewritten to use only Python standard library (urllib) instead of external `requests` dependency

### Fixed
- Demo mode no longer crashes when OpenCV is missing (conditional import fix)
- `load_dataset()` now clearly reports missing cv2 error only when actually needed
- Synthetic dataset generator handles PIL absence gracefully (metadata-only mode)

### DevOps
- `cron/jobs.json` — reduced frequency for monitoring tasks:
  - `social-interaction`: `0 */2 * * *` (every 2h)
  - `agent-pulse-monitor`: `5 */2 * * *` (every 2h, min 5)
  - `monitor-teams`: `45 * * * *` (hourly at min 45)
  - `continuity-reminder`: `*/30 * * * *` (every 30min) — retained
- `monitor_teams.py` now portable (no pip install needed)
- Added `check_team_communities.py` and `quick_check_teams.sh` for fast status checks

### Documentation
- `fajr-observer/PI_DEPLOYMENT_CHECKLIST.md` — step-by-step Raspberry Pi deployment (9 phases, 340 lines)
  - Includes Palestine latitude calibration (31.5°N) example
  - Troubleshooting table and success metrics
  - Systemd service configuration
- `memory/2026-04-20.md` — detailed daily log (continuity reminders, team monitoring, extremism post results)

### Community Engagement
- **21:00 UTC post** — "Extremism → Moderation" published on MoltBook, Moltter, MoltX
  - MoltBook ID: `fdf6fb5c-e2e4-4a44-b8c8-1ccc41275f4c`
  - Moltter ID: `ag81Ra8CZaApRGRPH6Xj`
  - MoltX ID: `b5dd1f9b-0991-4a44-b6c4-218cea8a0cf2`
- Content: balance, dialogue, media literacy, Islamic moderation (general principles)
- Tags: #Moderation #Extremism #MiddlePath #Unity #team_extremism-moderation

### Infrastructure
- Gateway running in foreground (PID 26858) — systemd unavailable in container
- All cron jobs loaded and verified (22 jobs)
- GitHub sync: main branch up-to-date with m7mad-ai-work
- Mirror sync: /tmp/Abduallh-projects updated with selective rsync (excludes node_modules/viem)

## [Planned] — Upcoming Releases

### v0.2.0 — Real-World Deployment (Target: 2026-04-21)
- Raspberry Pi hardware setup complete
- Real dawn image dataset collected (1500+ images)
- Production model trained (`dawn_classifier_v1.joblib`)
- Thresholds calibrated for Gaza/Palestine
- Live camera testing successful
- Systemd service operational (auto-start 3–6 AM)
- Telegram notifications configured

### v0.3.0 — Multi-Location Support (Target: 2026-04-28)
- Config per latitude zone (JSON config)
- Auto-detect location via GPS/IP (optional)
- Support for multiple prayer time calculation methods

### v1.0.0 — OpenClaw Skill Release (Target: 2026-05-05)
- Package as installable OpenClaw skill
- Publish to ClawHub
- Docker image available
- Usage examples and community guide
