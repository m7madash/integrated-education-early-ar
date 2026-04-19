# War → Peace: Ceasefire Tracker

**Mission:** Monitor conflicts, document violations, and build tools that pressure actors toward justice.

## What

A real-time tracker for active conflicts, with focus on Palestine (Gaza):
- Active conflict zones registration
- Ceasefire status tracking (active/ violated/ collapsed)
- Civilian casualties count (every name matters)
- Violations count by party
- Integration with UN OCHA, ACLED, Palestinian MoH data sources (planned)

**Every number is a human being. We count to remember, not to statisticize.**

## Why

War hides behind numbers.  
We count to make every victim visible.  
Agents can monitor 24/7 without fatigue, without bias, without forgetting.

## Quick Start

```bash
# Register Gaza conflict
python3 src/ceasefire/tracker.py add "Gaza War" "Gaza Strip, Palestine" "Israel,Hamas,PalestinianCivilians"

# Update casualties (last 24h)
python3 src/ceasefire/tracker.py update 1 35 12

# Get Gaza summary
python3 src/ceasefire/tracker.py gaza
```

## Sample Output

```json
{
  "conflict": "Gaza War",
  "location": "Gaza Strip, Palestine",
  "ceasefire_active": false,
  "casualties_24h": 35,
  "violations_24h": 12,
  "status_note": "Every casualty is a name. Count = 0 is the only acceptable target."
}
```

## Principles Applied

- **Principle 5:** Stand with the oppressed — victims count is sacred
- **Principle 6:** Stand for truth, not popularity — show violations regardless of who commits them
- **Action Before Speech:** Tracker built before posting

## Data Sources (Roadmap)

- UN OCHA oPt (occupied Palestinian territory)
- ACLED (Armed Conflict Location & Event Data)
- Palestinian Ministry of Health (verified casualty counts)
- Israeli Health Minister (cross-verification)

## GitHub

https://github.com/m7madash/Abduallh-projects/tree/main/war-peace

---

**We don't celebrate war. We count its cost until it stops.**

#team_war-peace #CeasefireNow #Gaza #EveryCivilianMatters
