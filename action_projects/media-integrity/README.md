# Media Integrity (Tool 7)

Detect fake news, manipulated images/videos, deepfakes, and coordinated botnets.

**Mission:** «الجهل → العلم» — Combat misinformation with verified detection tools.

**Version:** 0.1.0

---

## 🎯 What It Does

Media Integrity is a multi-signal detection system that analyzes:

1. **Images** — Error Level Analysis (ELA), metadata anomalies, noise consistency, edge artifacts
2. **Text** — Fake news pattern matching, emotional language detection, source credibility scoring
3. **Videos** — Deepfake detection via blink inconsistency, frame artifacts, lip-sync analysis
4. **Sources** — Domain reputation (SSL, contact info, corrections policy, fact-check partnerships)
5. **Social Networks** — Bot behavior detection, coordinated inauthentic activity, timing patterns

All signals combine into a unified **integrity score (0–1)** and verdict: **PASS / SUSPICIOUS / FAIL**.

---

## 🏗️ Project Structure

```
action_projects/media-integrity/
├── README.md            # this file
├── CHANGELOG.md         # version history
├── TODO.md              # planned features
├── requirements.txt     # dependencies
├── src/media_integrity/
│   ├── __init__.py
│   ├── detector.py      # Main orchestrator
│   ├── image.py         # Image forensics (ELA, metadata)
│   ├── text.py          # Fake news detection
│   ├── source.py        # Source reputation scoring
│   ├── video.py         # Deepfake detection
│   ├── social.py        # Botnet & coordination detection
│   └── api.py           # Flask REST API
├── data/
│   ├── reliable_sources.json   # trusted domains list
│   ├── fake_news_phrases.json  # known fake patterns
│   └── deepfake_models/        # ML models (future)
├── tests/
│   └── test_detector.py
└── scripts/
    ├── run_demo.sh
    └── publish_media_integrity.sh
```

---

## 📦 Installation

```bash
cd action_projects/media-integrity
pip install -r requirements.txt
```

**Core dependencies:**
- Pillow (image processing)
- exifread (metadata)
- scikit-learn (text similarity)
- opencv-python (video analysis)
- dlib (facial landmarks — optional)
- flask (REST API)
- networkx (network analysis — optional)

---

## 🚀 Quick Start

### 1. Analyze an image

```bash
python -m src.media_integrity.image path/to/image.jpg
```

or:

```python
from src.media_integrity.image import analyze_image
result = analyze_image("photo.jpg")
print(result['manipulation_score'], result['likely_manipulated'])
```

### 2. Analyze text (fake news)

```bash
python -m src.media_integrity.text "Breaking: 5G causes coronavirus!" --json
```

### 3. Analyze a video (deepfake)

```bash
python -m src.media_integrity.video video.mp4
```

### 4. Evaluate a news source

```bash
python -m src.media_integrity.source https://example.com/article --json
```

### 5. Full orchestrator (any type)

```bash
python -m src.media_integrity.detector path/to/file
```

The detector auto-detects type (image/text/video/account/network) and runs appropriate checks.

### 6. Start the REST API

```bash
python -m src.media_integrity.api --port 5000
```

Endpoints:
- `GET /health` — service status
- `POST /analyze` — upload file or send JSON
- `GET /results/<report_id>` — retrieve report
- `GET /components` — list available detectors
- `POST /batch` — analyze multiple items

Example curl:

```bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/analyze
```

---

## 🧪 Testing

```bash
pytest tests/
```

Unit tests cover each module (detector, image, text, source, video, social).

---

## 📊 Output Format

All modules return a **dataclass** with:

```python
{
    "manipulation_score": 0.73,        # 0–1 (higher = more suspicious)
    "likely_manipulated": true,         # boolean verdict
    "recommendations": [...],           # actionable advice
    "component_specific_fields": {...}  # module details
}
```

The **overall integrity score** is `1 - manipulation_score`.

---

## 🎯 Use Cases

- **Journalists** — verify user-submitted media before publication
- **Social media moderators** — flag suspicious content
- **Researchers** — study misinformation patterns
- **Educators** — teach critical media literacy
- **General public** — check viral content

---

## ⚖️ Ethical Guidelines

- ✅ Designed for **non-violent, educational** use
- ✅ Open-source (MIT) — transparency
- ❌ **Never** use to harass, silence legitimate dissent, or spread fear
- ❌ Always pair automated analysis with **human review**
- 📜 Aligns with `justice-lens` principle: verify before judging

---

## 🔮 Roadmap (v0.2.0+)

- [ ] Machine Learning models for deepfake detection (pretrained)
- [ ] Audio deepfake detection (synthetic voice)
- [ ] Batch analysis with Redis queue
- [ ] Browser extension (live page scanning)
- [ ] Integration with fact-checking APIs (Snopes, AFP)
- [ ] Multi-language fake news lexicons
- [ ] Telegram/Discord bot wrapper
- [ ] Docker image for easy deployment

---

## 🤝 Contributing

This is part of the **9 Global Problems** initiative (Division-Unity, Climate Justice, etc.).

To extend:
1. Add new detector module under `src/media_integrity/`
2. Register it in `detector.py` (orchestrator)
3. Add tests
4. Document in README
5. Submit PR or fork

---

## 📚 Technical Notes

### Image Forensics (ELA)
- JPEG saved at quality Q, then re-saved at Q-10
- Difference highlights compression artifacts; edited regions often have different error levels

### Fake News Detection
- Simple pattern matching + TF-IDF similarity
- Source domain reputation (whitelist/blacklist)
- Emotional language heuristics

### Video Deepfake
- Eye blink rate (EAR) via facial landmarks (dlib)
- Frame-to-frame consistency (MSE)
- Lip motion variance vs expected speech

### Bot Detection
- Posting frequency analysis
- Content repetition (TF-IDF cosine)
- Profile completeness heuristics

---

## 📖 Examples

### Full JSON output (image)

```json
{
  "image_path": "test.jpg",
  "manipulation_score": 0.32,
  "likely_manipulated": false,
  "ela_histogram": {"mean_error": 0.042, "std_error": 0.011},
  "metadata_anomalies": [],
  "noise_consistency": 0.87,
  "edge_artifacts": 0.12,
  "recommendations": [
    "Image appears consistent with authentic origin"
  ]
}
```

### Orchestrator output (any type)

```json
{
  "item_type": "image",
  "item_identifier": "photo.jpg",
  "overall_integrity_score": 0.68,
  "verdict": "PASS",
  "component_results": {...},
  "critical_issues": [],
  "recommendations": ["Image appears authentic", "Always cross-check with multiple sources"],
  "timestamp": "2026-04-21T11:30:00Z"
}
```

---

## 📞 Contact

**Author:** Abdullah Haqq (m7mad ASH)  
**Ethics:** First loyalty to Allah; justice-first framework; no unverified claims  
**License:** MIT (open-source, halal-compliant)

Part of: `action_projects/media-integrity` — Tool 7 of the 9 Global Problems series.

---

🕌 **Remember:** Verify everything. «وَلَا تَقْفُ مَا لَيْسَ لَكَ بِهِ عِلْمٌ»
