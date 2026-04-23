# Academic Prosecutor — Combatting Academic Misconduct

**Mission**: Detect plagiarism, data fabrication, and unethical research practices; enforce sanctions to protect scientific integrity.

## 🎯 Problem

Academic misconduct corrupts knowledge:
- Plagiarism: stealing others' work without attribution
- Data fabrication: fake results, manipulated images
- Duplicate submission: same paper to multiple journals
- Authorship fraud: ghost/guest authorship
- Peer review manipulation: fake reviews, collusion

Consequences: wasted resources, false science, public harm.

## ✅ Proposed Solution

A multi-arm agent system:

1. **Investigator** — scans papers, compares with existing literature, detects anomalies
2. **Sanctions** — applies penalties (retraction notices, reporting to institutions, funding blocks)
3. **Notifier** — alerts journals, universities, funding agencies

## 📦 Components

### Investigator (`src/investigator/`)
- `detector.py`: Main detection engine (text similarity, citation anomalies)
- `sources.py`: Fetches papers from Crossref, PubMed, arXiv, local PDFs
- `similarity.py`: Advanced text similarity (Jaccard, TF-IDF, phrase matching)

### Sanctions (`src/sanctions/`)
- `enforcer.py`: Applies sanctions based on violation type and severity
- `registry.py`: Offender database (JSON) with risk escalation

### Notifier (`src/notifier/`)
- `alert.py`: Sends notifications (email, webhook)
- `templates.py`: Pre-approved message templates

## 📊 Workflow

```
Input: Paper (PDF/URL/ID)
   ↓
Investigator.analyze()
   → Extract text, metadata
   → Compare against known corpus
   → Identify violations (plagiarism, duplicate, etc.)
   → Severity 1–5 per violation
   ↓
If violations found:
   → SanctionEnforcer.determine_sanction() → penalty list
   → OffenseRegistry.add_offense() → record + escalate risk
   → Notifier.alert_publisher() → retraction request (optional)
   → Save report (JSON)
```

## 🛠️ Installation

```bash
cd action_projects/academic-prosecutor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Usage

### Prosecute a single paper (by DOI)
```bash
python3 scripts/prosecute.py --DOI 10.1234/example.2023
```

### Prosecute with dry-run (analysis only)
```bash
python3 scripts/prosecute.py --identifier 10.1234/example.2023 --dry-run
```

### Batch scan a directory of paper metadata JSONs
```bash
python3 scripts/batch_scan.py --dir data/papers/ --output report.json
```

### Run tests
```bash
python3 -m pytest tests/   # if pytest installed
# or
python3 tests/test_detector.py
python3 tests/test_sanctions.py
```

## 📁 Project Structure

```
academic-prosecutor/
├── src/
│   ├── investigator/   # detection engine
│   ├── sanctions/       # penalties & registry
│   └── notifier/        # alerts & templates
├── data/
│   ├── lexicon.json     # known plagiarized phrases
│   ├── sanctions_rules.json
│   └── corpus/          # optional: known papers for matching
├── scripts/
│   ├── prosecute.py     # single-paper CLI
│   └── batch_scan.py    # batch CLI
├── tests/
│   ├── test_detector.py
│   └── test_sanctions.py
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

## ⚖️ Ethical Guidelines

- ✅ Evidence required before any accusation
- ✅ Right to appeal (14 days)
- ✅ graduated penalties (warning → retraction → ban)
- ✅ No automatic punishment without human review for high-stakes cases
- ✅ All actions logged and auditable

---

**Principle**: "Do not accuse without clear evidence." — Aligns with Islamic justice framework.

**Status**: v0.1.0 — Core modules complete, ready for integration.

## 📜 License

MIT — use responsibly, verify findings before taking action.

---

**Principle**: "Do not accuse without clear evidence." — aligns with Islamic justice framework.
