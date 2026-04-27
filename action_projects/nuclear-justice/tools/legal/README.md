# ✅ Legal Qaeda — Tool 2 of Nuclear Justice

**Status:** ✅ مكتمل (Complete) — tested, documented, and ready for deployment.

**Nonviolent legal pressure toolkit:** Generate ICJ applications, ICC indictments, and sanctions lists against nuclear weapons actors.

---

## 🎯 What It Does

Legal Qaeda automates the production of **legal documents** for international courts and sanctions committees. It does not litigate — it prepares the paperwork that human lawyers and courts can use.

**Components:**
1. **ICJ Case Builder** — Applications to the International Court of Justice (NPT Art VI breaches, threat of use)
2. **ICC Indictment Builder** — Draft charges for the International Criminal Court (aggression, war crimes)
3. **Sanctions List Generator** — Creates targeted sanctions recommendations (asset freeze, travel ban) in JSON/CSV formats for UN or national authorities

All outputs are **Markdown** or **structured data** ready for filing.

---

## 🔧 Installation

```bash
cd tools/legal
# No external dependencies beyond Python 3.8+
```

---

## 🚀 Usage

### ICJ Case Generator
```bash
python3 legal_qaeda_cli.py --tool icj \
  --applicant "Islamic Republic of Iran" \
  --respondent "State X" \
  --facts facts.json \
  --output case.md
```

`facts.json` format:
```json
[
  {"date":"2025-03-15","description":"Enrichment to weapons-grade","evidence":"Satellite Annex A"},
  {"date":"2025-04-01","description":"Threat to use nuclear weapons","evidence":"Transcript Annex B"}
]
```

Output: `case.md` — structured ICJ application with jurisdiction, facts, legal grounds, prayer for relief.

### ICC Indictment Generator
```bash
python3 legal_qaeda_cli.py --tool icc \
  --suspect "General X" \
  --title "Head of Strategic Forces" \
  --position "Commander, Nuclear Missile Command" \
  --nationality "State X" \
  --output indictment.md
```

Output: `indictment.md` — draft indictment for aggression, war crimes.

### Sanctions Generator
```bash
python3 legal_qaeda_cli.py --tool sanctions \
  --persons persons.csv \
  --organizations orgs.csv \
  --evidence "Satellite + procurement records" \
  --prefix sanctions_targets
```

CSV formats:
- `persons.csv` columns: name, title, organization, country, risk_score, sanction_type
- `organizations.csv` columns: name, type, country, risk_score, justification

Outputs: `sanctions_targets.json`, `sanctions_targets_persons.csv`, `sanctions_targets_orgs.csv

### Demo
```bash
cd tools/legal
./demo.sh
```

Runs all three tools with sample data and generates demo files.

---

## 🧪 Testing

All tools have automated test suites.

```bash
# Using built-in unittest (no external dependencies)
python3 -m unittest discover -s tests -p 'test_*.py' -v

# Or using pytest (if installed)
pytest -v
```

**Test coverage:**
- Sanctions list generation (JSON + CSV output validation)
- ICJ case structure and required sections
- ICC indictment charge formatting

**Current status:** ✅ All tests passing (8/8 on 2026-04-26)

---

## 📂 Project Structure

```
tools/legal/
├── legal_qaeda_cli.py      # Unified CLI entrypoint
├── demo.sh                 # Demo runner
├── README.md               # This file
├── src/
│   ├── icj/
│   │   └── case_builder.py     # ICJ application generator
│   ├── icc/
│   │   └── indictment_builder.py # ICC indictment generator
│   └── sanctions/
│       └── updater.py          # Sanctions list generator
├── tests/               # Automated tests (unittest/pytest)
│   ├── test_sanctions.py
│   ├── test_icj.py
│   └── test_icc.py
└── docs/
    └── sample_facts.json       # Example facts for ICJ case
```

---

## ⚖️ Legal Basis

- **ICJ:** NPT Article VI (disarmament obligation), UN Charter Art 2(4) (threat of force), ICJ 1996 Advisory Opinion (nuclear weapons generally illegal)
- **ICC:** Rome Statute Art 5(2) (aggression), Art 8 (war crimes), Art 25 (individual criminal responsibility)
- **Sanctions:** UN Security Council resolutions (e.g., 1718 on DPRK, 2231 on Iran), domestic authorities (OFAC, EU)

Our role: prepare filings; actual jurisdiction rests with courts. We do not claim legal authority — we provide **evidence packages** to legitimate authorities.

---

## 🛡️ Safety & Ethics

- ✅ No false evidence fabrication — templates require user-provided facts (verified)
- ✅ No vigilante prosecution — documents are drafts for official channels
- ✅ Discrimination — target only decision-makers, not civilian employees
- ✅ Transparency — all generated documents bear watermark: "Prepared by Legal Qaeda, Project OMAR — For lawful use only"

---

## 📊 Status & Verification

| Component | Status | Evidence |
|-----------|--------|----------|
| ICJ Case Builder | ✅ Complete | `demo_icj_case.md` generated |
| ICC Indictment Builder | ✅ Complete | `demo_icc_indictment.md` generated |
| Sanctions Generator | ✅ Complete | JSON + CSV outputs validated |
| Test Suite | ✅ Passing | 8/8 tests passed (2026-04-26) |
| Documentation | ✅ Complete | README, usage, examples |

**Last updated:** 2026-04-26
**Verified by:** continuity_30min check + manual unittest run

---

## 🎮 Demo

```bash
cd tools/legal
./demo.sh
```

Runs all three tools with sample data and generates demo files in the current directory.

---

**"The law is a weapon of the oppressed when wielded with precision."** — Legal Qaeda ethos
