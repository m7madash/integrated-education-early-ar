# Changelog

All notable changes to Media Integrity will be documented in this file.

## [0.1.0] — 2026-04-21

### Added
- **Image Forensics** module (`image.py`) — ELA, metadata analysis, noise consistency, edge artifacts
- **Fake News Detector** (`text.py`) — pattern matching, emotional language, source credibility
- **Source Reputation** (`source.py`) — domain age, SSL, contact info, corrections policy, citations
- **Video Deepfake Detection** (`video.py`) — frame artifacts, blink inconsistencies, lip-sync estimation
- **Bot & Network Analysis** (`social.py`) — single-account bot detection, coordinated inauthentic behavior
- **Orchestrator** (`detector.py`) — unified analysis across all modalities
- **Flask REST API** (`api.py`) — HTTP endpoints for analysis (single, batch, results lookup)
- Comprehensive README with usage examples
- Test suite structure (tests/)
- Demo scripts (scripts/run_demo.sh, publish script)

### Modules Summary
| Module | Purpose | Dependencies |
|--------|---------|--------------|
| image.py | Detect edited/manipulated images | Pillow, exifread |
| text.py | Fake news & misinformation detection | scikit-learn (optional) |
| source.py | Evaluate source credibility | requests (optional) |
| video.py | Deepfake detection | opencv-python, dlib (optional) |
| social.py | Botnet & coordination detection | networkx, scikit-learn (optional) |
| detector.py | Main orchestrator | all above |
| api.py | Flask REST interface | flask |

### Known Limitations
- `video.py` facial landmark analysis requires `dlib` and `shape_predictor_68_face_landmarks.dat`
- `text.py` similarity matching works best with sklearn installed
- `source.py` domain age check requires external WHOIS API (not implemented)
- No ML models yet for deepfake detection (heuristics only)
- In-memory report storage (API) — not persistent

---

## [Planned] v0.2.0

### In Progress
- [ ] Pretrained ML models for deepfake detection (integrate Deepware/ Microsoft Video Authenticator)
- [ ] Audio deepfake detection (synthetic voice, voice cloning)
- [ ] Batch analysis with Redis queue
- [ ] Browser extension for live page scanning
- [ ] Integration with external fact-checking APIs (Snopes, AFP Fact Check, Logically)
- [ ] Multi-language fake news lexicons (Arabic, Spanish, French, Indonesian)
- [ ] Telegram bot wrapper
- [ ] Docker image + docker-compose
- [ ] Persistent storage (PostgreSQL + pgvector for embeddings)
- [ ] Real-time monitoring dashboard
- [ ] Rate limiting & API key management
- [ ] Webhook notifications for critical findings
- [ ] Signature-based detection for known deepfake model artifacts

---

## [Planned] v0.3.0

- [ ] Federated learning for privacy-respecting model updates
- [ ] Cross-platform mobile app (React Native / Flutter)
- [ ] Integration with browsers' built-in safe browsing APIs
- [ ] Collaborative blocking lists (shared bot/hoax databases)
- [ ] Advanced network graph analytics (Community detection, influence scoring)
- [ ] Automated report generation (PDF summaries)

---

## Version Scheme
`MAJOR.MINOR.PATCH`
- MAJOR: breaking changes / new architecture
- MINOR: new modules, major features
- PATCH: bug fixes, small improvements

---

🕌 **Developed under the 9 Global Problems initiative — Ignorance → Knowledge.**
