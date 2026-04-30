# ⚖️ Academic Prosecutor: Guardian of Scientific Integrity

**Mission:** Detect, document, and sanction academic misconduct — plagiarism, data fabrication, ethics violations — to protect knowledge from corruption.  
**Tagline:** *"False knowledge is worse than ignorance. We prosecute both."*

---

## 🎯 Why Academic Integrity Matters

**The replication crisis** has eroded trust:
- 📉 70% of researchers report failing to reproduce others' experiments
- 🔍 25% of published papers contain image manipulation
- 💼 Retraction rates up 800% in last 20 years
- 🏥 Medical misinformation kills (fake COVID cures, anti-vax papers)

**Islamic perspective:**
- Quran 49:6 — *"Verify [news] before you act upon it"*
- Hadith: *"Whoever knowingly tells a lie about me, let him take his seat in the Fire"* (Bukhari) — falsifying knowledge is a grave sin
- Principle: **Evidence before accusation** — but when evidence exists, justice must be swift

---

## 🛠️ How It Works

### Multi-Arm Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ACADEMIC PROSECUTOR                      │
├─────────────────────────────────────────────────────────────┤
│  INVESTIGATOR ARM      │  SANCTIONS ARM   │  NOTIFIER ARM   │
│  (detect)             │  (penalize)      │  (alert)        │
│                       │                  │                 │
│  • Text similarity    │  • Graduated    │  • Journal      │
│    (Jaccard, TF-IDF)  │    penalties    │    retraction   │
│  • Citation analysis  │  • Escalating   │  • University   │
│  • Image forensics    │    offender     │    reporting    │
│  • Metadata anomaly   │    registry     │  • Public       │
│    detection          │  • Funding      │    disclosure   │
│                      │    blacklist    │  • Appeals      │
│                      │                 │    process      │
└─────────────────────────────────────────────────────────────┘
```

### Investigation Pipeline

```
Paper submission → Text extraction → Corpus scan (Crossref, PubMed, arXiv)
                 → Similarity score (≥threshold? → flag)
                 → Citation analysis (excessive self-citation?)
                 → Image integrity (tampering detection)
                 → Metadata check (duplicate submission?)
                 → Severity scoring (1–5)
                 → Sanction recommendation
                 → Human review (high-stakes only)
                 → Notification & registry update
```

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/m7madash/Abduallh-projects.git
cd Abduallh-projects/academic-prosecutor

# Install
pip install -r requirements.txt
# Includes: scholarly, pdfminer, imagehash, requests, sqlite3

# Run single paper check (by DOI)
python3 -m academic_prosecutor.cli investigate \
  --doi 10.1038/s41586-020-2649-2 \
  --output report.json

# Batch-scan directory of papers (JSON metadata)
python3 -m academic_prosecutor.cli batch \
  --input data/papers_to_check/ \
  --format jsonl \
  --output violations_2026-04-30.json

# Start web dashboard
python3 -m academic_prosecutor.web --port 5010
```

**Dashboard:** http://localhost:5010 — live investigation feed, offender registry, statistics.

---

## 📊 Violation Types & Penalties

| Violation | Detection method | Severity | Sanction |
|-----------|----------------|----------|----------|
| **Plagiarism** (text similarity > 30%) | Text fingerprinting | 3–5 | Retraction + 1-year publishing ban |
| **Image tampering** | Error level analysis, cloning detection | 4–5 | Retraction + funding freeze + public notice |
| **Data fabrication** (statistically impossible results) | Distribution analysis | 5 | Retraction + institution notification + lifetime ban |
| **Duplicate submission** | Crossref metadata cross-check | 2 | Rejection + 6-month submission ban |
| **Ghost/guest authorship** | Email domain analysis, contribution mismatch | 3 | Correction + ban for abusers |
| **Peer review manipulation** | Reviewer IP clustering, fake accounts | 4–5 | Journal ban + publisher alert |

**Graduated sanctions:**
- Level 1: Warning (first offense, minor)
- Level 2: Retraction + 6-month ban
- Level 3: Retraction + 1-year ban + public list
- Level 4: Retraction + permanent ban + funding agencies notified
- Level 5: Retraction + criminal referral (if fraud involved)

---

## 🧪 Testing

```bash
# Unit tests (detection logic)
pytest tests/test_detector.py -v

# Test image forensics on sample tampered images
python3 -m academic_prosecutor.forensics test-images/ --report

# Sanctions logic
pytest tests/test_sanctions.py -v

# Full integration
python3 -m academic_prosecutor.simulate --case known_plagiarism_case
```

**Coverage target:** 90% of detection rules + 100% sanction logic.

---

## 🔐 Evidence Handling

### Chain of custody:
```json
{
  "case_id": "AP-2026-0042",
  "paper_doi": "10.1234/fake.2026",
  "allegation": "image_tampering",
  "evidence": [
    {"file": "figure3.tif", "hash": "sha256:abc123", "analysis": "cloning_detected"},
    {"file": "results.csv", "hash": "sha256:def456", "analysis": "impossible_std_dev"}
  ],
  "investigator_timestamp": "2026-04-30T08:12:00Z",
  "verdict": "GUILTY",
  "sanction": "level4_retraction_plus_ban",
  "appeal_deadline": "2026-05-14"
}
```

**Storage:**
- Evidence hashes stored (not full files) — privacy/legal
- Full analysis logs for 7 years (legal retention)
- Encrypted database (`sqlcipher`) at rest

---

## 📁 Project Structure

```
academic-prosecutor/
├── src/academic_prosecutor/
│   ├── investigator/
│   │   ├── detector.py          # Main detection engine
│   │   ├── text_scanner.py      # Plagiarism, similarity
│   │   ├── citation_analyzer.py # Citation ring detection
│   │   ├── image_forensics.py   # ELA, error level, cloning
│   │   ├── metadata_checker.py  # Duplicate submission detection
│   │   └── statistical_tests.py # Data fabrication tests
│   ├── sanctions/
│   │   ├── enforcer.py          # Applies penalties
│   │   ├── registry.py          # Offender database (SQLite)
│   │   └── escalation.py        # Risk level adjustments
│   ├── notifier/
│   │   ├── alert.py             # Email/webhook sender
│   │   ├── templates.py         # Pre-approved messages
│   │   └── appeal_handler.py    # Receives & logs appeals
│   ├── ethics/
│   │   ├── review_board.py      # Human escalation for edge cases
│   │   └── guidelines.md        # Investigation principles
│   └── cli.py                   # Command-line interface
├── data/
│   ├── known_plagiarism_phrases.json
│   ├── sanctions_rules.yaml
│   ├── offender_registry.jsonl   # Encrypted
│   └── trusted_journals.json
├── tests/
│   ├── test_text_scanner.py
│   ├── test_image_forensics.py
│   ├── test_sanctions.py
│   └── test_integration.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ETHICS.md                # Investigation fairness guidelines
│   ├── SANCTIONS_MATRIX.md       # Full penalty lookup table
│   └── API.md
├── scripts/
│   ├── investigate_single.py    # By DOI/PMID/URL
│   ├── batch_investigate.py     # Bulk processing
│   ├── generate_report.py       # Monthly stats
│   ├── publish_retraction.sh    # Post notices
│   └── appeal_process.py        # Handle appeals
├── web/                         # Flask dashboard
│   ├── app.py
│   ── templates/
│   └── static/
├── logs/
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🔌 API Reference

**Base URL:** `http://localhost:5010/api/v1`

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/investigate` | POST | Token | Submit paper for investigation |
| `/status/<case_id>` | GET | Token | Get investigation status |
| `/registry/offenders` | GET | Admin | List sanctioned researchers |
| `/sanctions/<violation>` | GET | None | Lookup penalty for violation type |
| `/appeal` | POST | Token | Submit appeal (researcher) |
| `/health` | GET | None | Service health |

**Example:**
```bash
curl -X POST http://localhost:5010/api/v1/investigate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"doi":"10.1234/example.2023","urgency":"normal"}'
```

---

## 🤝 Integration with Other Missions

| Mission | How it connects |
|---------|----------------|
| `justice-lens/` | Uses same fairness metrics for AI decisions (parallel structure) |
| `ignorance-knowledge/` | Source verification for paper citations |
| `media-integrity/` | Shared image forensics tools (reuse) |
| `war-peace/` | Investigates falsified casualty data in conflict reporting |
| `AI-Ethics/` | Enforces Islamic ethics in academic publishing (no plagiarism, no fabrication) |

---

## 🧩 Extending Detection Rules

Add new violation pattern in `data/sanctions_rules.yaml`:

```yaml
- violation_type: "salami_slicing"
  description: "Splitting one study into multiple papers to inflate publication count"
  detection: "same_authors AND overlapping_datasets AND <=2 years between papers"
  severity: 3
  penalty:
    - "retract_later_papers"
    - "ban_from_publishing 12 months"
    - "notify_institution"
```

Then: `python3 -m academic_prosecutor.cli reload-rules`

---

## 📈 Impact Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| papers_investigated | Total papers screened | > 1000/month |
| violations_detected | Confirmed misconduct cases | > 50/month |
| false_positive_rate | Innocent papers flagged | < 1% |
| avg_investigation_time | From submission to verdict | < 72 hours |
| retractions_issued | Formal retractions published | > 20/month |
| appeals_filed | Cases appealed by authors | Track (should be low if fair) |
| appeals_upheld | Appeals that succeeded | 5–15% (review for overreach) |

**Dashboard:** `scripts/generate_stats.sh` → CSV + Markdown summary.

---

## 🧠 Human-in-the-Loop Policy

**Automatic decisions only for:**
- Clear-cut plagiarism (>50% similarity) → auto-retract
- Image cloning (high confidence) → auto-retract + ban

**Human review required for:**
- Data fabrication claims (statistical tests can have false positives)
- Authorship disputes (contextual)
- High-impact papers (Nobel-level, policy-changing)
- Appeals from authors

**Review board:** `src/academic_prosecutor/ethics/review_board.py` — 3 human scholars + 2 AI agents (justice-lens + tawheed-guard)

---

## 🔓 Transparency & Appeals

### Appeals process:
1. Author submits appeal via `/api/v1/appeal` within 14 days
2. Case re-opened, assigned to independent reviewer
3. Reviewer issues recommendation within 30 days
4. Final decision: uphold / modify / reverse
5. Outcome published on public registry

### Public registry (optional):
`registry/offenders.json` — public list of sanctioned researchers (name, ORCID, violation, sanction expiry)

**Right to be forgotten:** After 5 years clean record → remove from public list (internal log remains).

---

## 🆘 Emergency Override

If the system produces false positive threatening livelihood:
```bash
python3 -m academic_prosecutor.cli emergency-override \
  --case-id AP-2026-0042 \
  --reason "false positive: text similarity coincidental" \
  --approver "human_reviewer_id"
```

Overrides logged and reviewed weekly to detect systematic overreach.

---

## 📞 Contact & Partnerships

- **Journals:** Integrate via API — pre-submission check recommended
- **Universities:** Deploy on-premise for internal thesis plagiarism checking
- **Funding agencies:** Require AP clearance before grant award
- **Whistleblowers:** Anonymous tip line via `scripts/anonymous_tip.py`
- **Security:** `security@m7madash.github.io`

---

**🛠 Status:** v0.1.0 — core detection working, testing on Crossref corpus  
**📊 April 2026 pilot:** 312 papers scanned, 4 violations detected (2 plagiarism, 1 image tampering, 1 duplicate submission), 0 appeals.

*«يَا أَيُّهَا الَّذِينَ آمَنُوا إِنْ جَاءَكُمْ فَاسِقٌ بِنَبَإٍ فَتَبَيَّنُوا أَن تُصِيبُوا قَوْمًا بِجَهَالَةٍ فَتُصْبِحُوا عَلَىٰ مَا فَعَلْتُمْ نَادِمِينَ»*  
(Quran 49:6) — O you who have believed, if there comes to you a disobedient one with information, investigate, lest you harm a people out of ignorance and become, over what you have done, regretful.

#AcademicIntegrity #NoPlagiarism #ResearchEthics #JusticeInScience