# Extremism → Moderation — Development Roadmap

## MVP (v0.1.0) — Done ✅
- [x] ExtremismDetector: lexicon (25+ terms) + patterns (8 regex) → score 0-100
- [x] ModerationResponder: tiered responses (critical/high/medium/low)
- [x] Knowledge base (4 extremism types, sources cited)
- [x] Islamic middle-path principles (9 Quran/Hadith-sourced)
- [x] Privacy module (anonymize, encrypt, report IDs)
- [x] CLI interactive (Arabic/English)
- [x] 8 passing tests
- [x] Demo script
- [x] Full docs (README, TODO, CHANGELOG, dev log)
- [x] Ready for 21:00 mission post + 19:00 dev snapshot (actually built early)
- [x] Push to GitHub

---

## v0.2.0 — Next (2 weeks)
- [ ] Arabic NLP for dialectal variations (Palestinian, Gulf, Egyptian)
- [ ] ML classifier (BERT fine-tune on extremist speech datasets)
- [ ] Multi-language: add French, Urdu, Indonesian
- [ ] Bulk text analysis (CSV/JSON upload)
- [ ] FastAPI web endpoint for agent-to-agent queries
- [ ] integrate with fact-checking skill (verify-claims)

---

## v0.3.0 — Monthly
- [ ] Web dashboard for human moderators
- [ ] Real-time chat integration (Telegram, Discord, Slack bots)
- [ ] Escalation workflow: auto-flag → human review → action
- [ ] User warning system (progressive discipline: warn → temp mute → ban)
- [ ] Appeal mechanism: allow users to contest moderation decisions
- [ ] Moderator training module (interactive lessons)

---

## v0.4.0 — Quarterly
- [ ] Multimodal: images, memes, videos (symbolism detection)
- [ ] Network graph: map radicalization connections between users
- [ ] Predictive modeling: early warning for radicalization pathways
- [ ] Partnership with counter-extremism NGOs (share anonymized trends)
- [ ] Mobile app for field monitors (offline-first)

---

## Never (Ethical Boundaries)
- ❌ Do NOT store user content with PII — always anonymize
- ❌ Do NOT label individuals as "extremists" — only label content/behavior
- ❌ Do NOT build surveillance state — transparency to users about what is flagged
- ❌ Do NOT remove speech without clear policy and appeal process
- ❌ Do NOT train on private user data without explicit consent
- ❌ Do NOT collaborate with regimes that use "extremism" to silence dissent

---

**Mission**: Balance. Middle path. Justice.
**Action Before Speech**: MVP ready before 21:00 mission post.