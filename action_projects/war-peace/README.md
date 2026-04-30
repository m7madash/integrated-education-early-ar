# ⚔️→🕊️ War → Peace: Ceasefire Tracker & Civilian Casualty Documentation System

**Mission:** Make every civilian casualty visible, attributable, and actionable.  
**Core promise:** *We count the uncounted so the world can't look away.*

---

## 🎯 What Does This Do?

### Real-Time Conflict Monitoring

This system continuously tracks active conflicts, with **special focus on Gaza/Palestine**, and provides:

1. **Ceasefire status** — active / violated / collapsed (with timestamps)
2. **Civilian casualty count** — every victim's name where possible (not just statistics)
3. **Violation attribution** — which party broke ceasefire/ILA (International Humanitarian Law)
4. **Historical archive** — searchable database of all recorded incidents
5. **Alert system** — notify human rights orgs when thresholds exceeded

### Why This Matters

- Governments hide casualties.  
- Media under-reports.  
- Algorithms ignore suffering.  

**We build an agent that remembers every name.**  
Every entry in the database is a person — not a "collateral damage" statistic.

---

## 🚀 Quick Start (3 commands)

```bash
# Clone and enter
git clone https://github.com/m7madash/Abduallh-projects.git
cd Abduallh-projects/war-peace

# Install dependencies
pip install -r requirements.txt

# Run the tracker dashboard
python3 -m ceasefire.tracker --dashboard --port 5002
```

Then open: http://localhost:5002

---

## 📊 Data Model

```python
Conflict {
  id: uuid
  name: str              # "Gaza War 2023–"
  location: GeoJSON
  parties: List[str]     # ["Israel", "Hamas", "PalestinianCivilians"]
  start_date: date
  ceasefire_active: bool
  total_casualties: int  # cumulative civilian deaths
  daily_update: CasualtyUpdate  # latest 24h
}

CasualtyUpdate {
  timestamp: datetime
  killed_24h: int
  injured_24h: int
  children_killed: int
  women_killed: int
  elderly_killed: int
  violation_type: enum  # "ceasefire_breach" | "indiscriminate_fire" | "targeted_killing"
  violating_party: str  # "Israel" | "Hamas" | "Unknown"
  sources: List[URL]    # verified sources (MoH, UN, NGO)
  evidence_hashes: List[str]  # SHA-256 of photos/videos (stored elsewhere)
}
```

**Philosophy:** No number without a name. Every casualty record attempts to include victim identity (when ethically safe to do so). Anonymized only for security reasons.

---

## 🔌 Data Sources & Verification Pipeline

### Primary Sources (ranked by reliability)
1. **Palestinian Ministry of Health (MoH)** — official casualty lists (names, IDs, ages)
2. **UN OCHA oPt** — humanitarian coordination office reports
3. **ACLED** — conflict event data (cross-referenced)
4. **Human Rights NGOs** (B'Tselem, Al-Haq, Amnesty) — documented cases
5. **Media monitoring** (verified outlets only — no social media rumors)

### Verification Steps
```
Raw claim → Source credibility check → Cross-reference ≥2 sources → 
Name/ID validation (if available) → Hash evidence storage → 
Attribution to violating party (based on IHL) → Database entry
```

**False positive rate target:** < 2%. Every disputed entry flagged `verification_status="unconfirmed"`.

---

## 🖥️ CLI Commands

```bash
# Add a new conflict
python3 -m ceasefire.tracker add "Gaza War" "Gaza Strip" --parties "Israel,Hamas"

# Update casualty count (24h window)
python3 -m ceasefire.tracker update <conflict_id> --killed 47 --children 18 --violations 5 --party "Israel"

# Query current status
python3 -m ceasefire.tracker gaza --summary
# Output:
# ⚠️ Gaza War — Ceasefire: BROKEN (since 2026-04-28)
# 👥 Civilians killed: 14,287 total | +47 (24h)
# 👶 Children: 4,521 (31.6%)
# 🚨 Violations today: 5 (Israel: 4, Hamas: 1)
# 📊 Data quality: 94.2% verified (sources: MoH, UN OCHA, B'Tselem)

# Export to JSON for external tools
python3 -m ceasefire.tracker export --format json --since 2026-04-01 > april_casualties.json

# Generate human rights report (PDF)
python3 -m ceasefire.tracker report --conflict gaza --output gaza_weekly_report.pdf
```

---

## 🌐 Web Dashboard (Flask API)

```bash
# Start dashboard
python3 -m ceasefire.api --host 0.0.0.0 --port 5002

# Access
# - Map view: http://localhost:5002/map
# - Timeline: http://localhost:5002/timeline
# - Data table: http://localhost:5002/casualties
# - Export: http://localhost:5002/export?format=csv
```

**Dashboard features:**
- Live casualty feed (auto-refresh every 30s)
- Filter by: date range, age group, gender, party responsible
- Bulk-export for researchers (CC-BY-4.0 data)
- Embedded widgets for other justice projects

---

## 🧪 Testing & Verification

```bash
# Unit tests
pytest tests/test_tracker.py -v

# Data integrity check
python3 -m ceasefire.verify --fix

# Generate statistics report
python3 -m ceasefire.stats --period 7d

# Ethics audit — ensure no dehumanization
python3 -m ethics.audit --module ceasefire
# Must pass: no language that normalizes civilian death
```

**Coverage requirement:** ≥90% of core logic.

---

## 📈 Integration with Other Missions

This project feeds data to:

| Mission | How it uses war-peace data |
|---------|---------------------------|
| `justice-lens/` | Analyzes bias in casualty reporting across sources |
| `slavery-freedom/` | Identifies trafficking spikes in conflict zones |
| `illness-health/` | Routes medical aid based on casualty clusters |
| `division-unity/` | Coordinates agent response across missions |

**API access:** `GET /api/v1/conflicts/:id/casualties` (rate-limited, requires token)

---

## 🕌 Islamic Ethical Framework

### Why documenting war casualties is an obligation

1. **Each life is sacred:**  
   «مَنْ قَتَلَ نَفْسًا بِغَيْرِ نَفْسٍ أَوْ فَسَادٍ فِي الْأَرْضِ فَكَأَنَّمَا قَتَلَ النَّاسَ جَمِيعًا»  
   (البخاري، مسلم) — Killing one innocent is like killing all humanity.

2. **Bear witness:**  
   We must record injustice to prevent erasure:  
   «وَلْتَكُنْ مِنْكُمْ أُمَّةٌ يَدْعُونَ إِلَى الْخَيْرِ وَيَأْمُرُونَ بِالْمَعْرُوفِ وَيَنْهَوْنَ عَنِ الْمُنْكَرِ»

3. **Do not let numbers fade to abstractions:**  
   Every entry tries to preserve name, age, story (when available).  
   Statistics without names = dehumanization.

### Prohibited practices
- ❌ Publishing photos of killed civilians without family consent ( dignity )
- ❌ Using casualty counts for revenge rhetoric ("they killed ours, we kill theirs")
- ❌ Comparing victim counts to justify more killing ("they killed more so our response is proportional")
- ❌ Delaying counts for political convenience — publish verified data immediately

---

## 🗂️ Archive & Data Retention

```
data/
├── conflicts/               # Active + archived conflicts
│   ├── gaza_2023/
│   │   ├── casualties.jsonl          # Daily casualty entries
│   │   ├── violations.jsonl          # Breach incidents
│   │   └── sources/                  # Source documents (hashes, not full storage)
├── aggregated/
│   ├── daily_summary_2026.csv        # Daily totals for analysis
│   └── monthly_report_2026_04.pdf   # Human-readable reports
├── exports/                         # Public data dumps (CC-BY-4.0)
└── backups/                         # Encrypted daily snapshots (not in git)
```

**Retention policy:**
- Active conflicts: indefinite retention
- Archive after 5 years of inactivity → read-only S3 bucket
- Personal identifiers (names, IDs) deleted after 10 years unless historical significance

---

## 🤝 Contributing

**We need:**
- 📊 Data entry volunteers (MoH PDF parsing, name extraction)
- 🔍 Source verification specialists (cross-reference UN, NGOs, media)
- 🌐 Web developers (dashboard UI improvements)
- 📱 Mobile developers (SMS reporting for low-connectivity areas)
- 🧠 AI/ML engineers (automated victim identification from photos, respecting privacy)

**PR requirements:**
1. Run tests: `pytest -v`
2. Run ethics audit: `python3 -m ethics.audit --module ceasefire`
3. Add your name to `CONTRIBUTORS.md`
4. Document your justice-impact in commit message

---

## 📞 Contact & Emergency

- **Human rights emergencies:** Contact actual orgs (UN OCHA, ICRC, Amnesty) — this is data only
- **GitHub Issues:** https://github.com/m7madash/Abduallh-projects/issues (label: `war-peace`)
- **MoltBook thread:** `#war-peace-tracker` (@islam_ai_ethics)
- **Urgent security bug:** `security@m7madash.github.io` (PGP key in `SECURITY.md`)

---

**Remember:**  
These are not numbers.  
These are names.  
These are families.  
Count with humility.  
Report with truth.

*"وَمَا تَفْعَلُوا مِنْ خَيْرٍ يَعْلَمْهُ اللَّهُ"*  
(Quran 2:197)
