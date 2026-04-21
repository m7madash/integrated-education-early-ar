# TODO — Media Integrity (Tool 7)

## 🔴 Critical / Blocking

- [ ] Add `shape_predictor_68_face_landmarks.dat` download instructions for video deepfake (dlib)
- [ ] Make `video.py` work without dlib (fallback to simpler heuristics)
- [ ] Add error handling for missing optional dependencies (graceful degradation)
- [ ] Fix `social.py` DBSCAN import error (import inside try block)
- [ ] Implement persistence for API reports (replace in-memory dict with Redis/DB)
- [ ] Add rate limiting to API
- [ ] Add API authentication (API keys)
- [ ] Add CORS headers to Flask API for web frontends

## 🟡 High Priority

- [ ] Train/ship a basic deepfake detection model (use existing open-source weights)
- [ ] Integrate with external fact-check APIs (Snopes, FactCheck.org, AFP)
- [ ] Add Arabic language support for fake news lexicon
- [ ] Build Telegram bot wrapper
- [ ] Create Dockerfile + docker-compose.yml
- [ ] Write comprehensive unit tests for each module (≥80% coverage)
- [ ] Add logging infrastructure (structured logs)
- [ ] Create demo notebook (Jupyter) showing full pipeline

## 🟢 Medium Priority

- [ ] Add audio analysis (voice cloning detection)
- [ ] Implement WHOIS lookup for domain age
- [ ] Add image metadata stripping check (does image have original metadata?)
- [ ] Build browser extension (Firefox/Chrome) that uses local API
- [ ] Create public demo page (Streamlit/Gradio)
- [ ] Integrate with Common Crawl for historical page comparison
- [ ] Add support for PDF documents (text extraction + image analysis inside PDF)
- [ ] Network timeline visualization (interactive HTML)

## 🔵 Low Priority / Future

- [ ] Federated learning: improve models without central data collection
- [ ] Cross-platform mobile app
- [ ] Automated screenshot analysis (full-page rendering + integrity check)
- [ ] Integration with safe browsing APIs (Google, Yandex)
- [ ] Collaborative blocking lists (P2P sync)
- [ ] Support for AI-generated text detection (GPT detectors)
- [ ] Multi-modal fusion: score aggregation across image+text+source
- [ ] Automated takedown request generation (for confirmed fakes)
- [ ] Webhook notifications for monitoring

---

## 📅 Current Sprint (v0.1.0)

**Week of 2026-04-21:**
- [x] Core modules (image, text, source, video, social)
- [x] Orchestrator (detector.py)
- [x] Flask REST API (api.py)
- [x] README, CHANGELOG, basic tests
- [ ] Bugfixes (imports, optional deps)
- [ ] Deploy test instance locally
- [ ] Write integration test (end-to-end)

---

## 🧩 Module Owners (for multi-agent handoff)

| Module | Owner Agent (planned) | Status |
|--------|----------------------|--------|
| image.py | MediaImageAgent | Complete |
| text.py | MediaTextAgent | Complete |
| source.py | MediaSourceAgent | Complete |
| video.py | MediaVideoAgent | Complete |
| social.py | MediaSocialAgent | Complete |
| detector.py | MediaOrchestratorAgent | Complete |
| api.py | MediaAPIAgent | Complete |

---

🕌 **Developed under Islamic ethics: no fabrication, no harm, no spying. Only verify with evidence.**
