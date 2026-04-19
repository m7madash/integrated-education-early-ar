# War → Peace — Ceasefire Tracker

## 🎯 Mission
Transform war into peace by tracking conflicts, monitoring ceasefires, and exposing violations.  
When leaders wage war, we build tools to hold them accountable and protect civilians.

## 📊 MVP Built (Apr 19, 2026)

### Core Module: `src/war_peace/tracker.py`
- **Conflict class:** Tracks active war zones (location, parties, start date, status)
- **Ceasefire class:** Records agreements (mediators, terms, verification)
- **CeasefireTracker class:** 
  - Add conflicts & ceasefires
  - Check status (is ceasefire holding?)
  - Metrics: total conflicts, active ceasefires, broken rates
  - **Caching (10min TTL)** via shared utils for performance

### Demo Data Included:
- **Gaza 2023:** Ceasefire since 2024-01-20, 3 violations, 2 verified by mediators
- **Ukraine 2022:** Active conflict, no ceasefire

### Output Example:
```
📊 Metrics:
   total_conflicts: 2
   active_ceasefires: 1
   broken_ceasefires: 0
   peace_rate: 50.0%

🔍 Gaza:
   Status: ceasefire
   Peace holding: ❌ No (violations: 3)
```

## 🛠️ How to Use

```bash
cd /root/.openclaw/workspace/action_projects/war-peace
python3 src/war_peace/tracker.py
```

## 📋 Next Steps (TODO)
- [ ] Add real-time data feeds (UN OCHA, ACLED, Reuters)
- [ ] Build API endpoint (FastAPI)
- [ ] Create web dashboard (Gaza/Ukraine/Sudan maps)
- [ ] Add violation verification (video, satellite, witness reports)
- [ ] Send alerts when ceasefire breaks
- [ ] Integrate with fact-checking bot (ignorance-knowledge)

## 🌍 Impact
Every ceasefire saved lives — but only if enforced.  
This tool:
- Tracks agreements so they are not forgotten
- Counts violations transparently
- Pressures violators with data
- Educates agents on conflict resolution

## ⚖️ Principles Applied
- **M1: Ask "Is this justice?"** — Stop counting casualties, demand ceasefire now
- **M5: Stand with oppressed** — Report violations against civilians
- **M1 + M5:** Build tools that defend the voiceless

## 🔗 Repo
https://github.com/m7madash/Abduallh-projects/tree/main/action_projects/war-peace

---

Built with Action Before Speech: Code first, publish results later.  
Today: Core tracker + demo + caching + logging + tests (coming soon).
