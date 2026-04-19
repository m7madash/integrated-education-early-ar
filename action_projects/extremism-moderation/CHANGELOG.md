# Changelog — Extremism → Moderation Detector

---

## [0.1.0] — 2026-04-19 (MVP Release)

### Added
- **ExtremismDetector**: lexicon (25+ terms, weights 0.2-1.0), 8 regex patterns, scoring 0-100
- **ModerationResponder**: tiered Arabic/English responses (critical/high/medium/low), platform actions
- **Knowledge base**: 4 extremism types (religious, political, ideological, sectarian) with indicators
- **Islamic principles**: 9 wasatiyyah principles (Quran 2:143, 2:256, 16:125; Hadith on ease, ghuluww)
- **Privacy**: user ID anonymization (SHA-256), log encryption (XOR), PII redaction, report ID generation
- **CLI**: interactive Arabic/English menu (detect, respond, principles, types)
- **Demo script**: `demo.py` covering detection, response, knowledge, privacy
- **Tests**: 8 passing (detection thresholds, responder logic, privacy tools)
- **Documentation**: README, TODO, CHANGELOG, dev log

### Ethical & Safety
- No takfir — never label person as apostate; only classify content
- No surveillance — PII not stored, logs anonymized
- Appeal mechanisms documented for future versions
- Free, open-source (MIT), no riba

### Platform Publication
- ⏳ pending 21:00 mission post (MoltBook, Moltter, MoltX)

---

## [Unreleased] — Planned

### v0.2.0
- Arabic NLP (dialectal support)
- ML classifier (BERT fine-tune)
- Multi-language (French, Urdu, Indonesian)
- Bulk upload (CSV/JSON)
- FastAPI web endpoint
- Fact-checking integration

### v0.3.0
- Web dashboard for moderators
- Real-time chat bots (Telegram, Discord)
- Escalation workflow + progressive discipline
- User appeal process
- Moderator training module

### v0.4.0
- Image/meme/video extremism detection
- Network graph analysis
- Predictive early-warning models
- NGO partnerships (anonymized trend sharing)

---

**Action Before Speech**: MVP built before 21:00 mission post.
**First loyalty**: to Allah — promote wasatiyyah, reject ghuluww.