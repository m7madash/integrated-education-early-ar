# War → Peace — TODO

## 🎯 Mission
Build Ceasefire Tracker: monitor conflicts, track ceasefires, count violations, pressure violators with data.

## 📋 Current Tasks (Apr 19, 2026)

### ✅ Completed (Today - Action Before Speech)
- [x] Created project structure (`src/war_peace/`)
- [x] Built `tracker.py` core module
  - Conflict class
  - Ceasefire class  
  - CeasefireTracker with metrics
  - Status checking (peace_holding detection)
- [x] Created CLI (`src/war_peace/cli.py`)
- [x] Created tests (`tests/test_tracker.py`) — **4/4 passing**
- [x] Updated README with MVP details
- [x] Wrote dev log for Apr 19

### 🔄 In Progress
- [ ] Add real data sources (UN OCHA API, ACLED CSV, Reuters RSS)
- [ ] Build FastAPI endpoint (`/api/conflicts`, `/api/metrics`)
- [ ] Create web dashboard (Gaza/Ukraine/Sudan maps with leaflet.js)
- [ ] Add violation verification pipeline (video analysis, satellite imagery)
- [ ] Alert system (Telegram/Discord webhook on ceasefire break)
- [ ] Integrate with Ignorance → Knowledge fact-checking bot

### 📅 Future
- [ ] Deploy to cloud (Railway/Render)
- [ ] Add multi-language support (Arabic, English, French)
- [ ] Historical data archive (all conflicts since 2000)
- [ ] Partner with peace NGOs for data sharing

## 📊 Progress

| Area | % | Notes |
|------|---|-------|
| Design | 100% | Core classes architected |
| Implementation | 40% | MVP working, need API + dashboard |
| Testing | 100% | 4 tests passing |
| Documentation | 80% | README + this TODO + CHANGELOG |
| Deployment | 0% | Local only |

## 🎯 Next Immediate Step
Add FastAPI server with two endpoints:
- `GET /api/conflicts` — list all conflicts
- `GET /api/metrics` — summary stats

Then deploy to Railway.app for public access.

---

Last updated: 2026-04-19
