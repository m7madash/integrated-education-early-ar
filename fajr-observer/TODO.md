# Fajr Observer — Development Roadmap

## ✅ Completed (Phase 1: Prototype)
- [x] Core pipeline: camera → features → classifier → adhan
- [x] Rule-based classifier with configurable thresholds
- [x] Training script (SVM/RandomForest) with sklearn
- [x] Hand-crafted optical features (9 features)
- [x] Integration tests
- [x] Full documentation (README, USER_GUIDE, deployment_guide)
- [x] Demo mode (`--demo`) works without OpenCV
- [x] Synthetic dataset generator (PIL optional, metadata-only fallback)
- [x] Raspberry Pi deployment checklist (PI_DEPLOYMENT_CHECKLIST.md)
- [x] Conditional cv2 import (headless-friendly)
- [x] All code pushed to GitHub (m7mad-ai-work)

## 🔄 In Progress (Phase 2: Hardware Deployment)
- [ ] Raspberry Pi setup (OS Lite, enable camera, SSH)
- [ ] Install dependencies (`install_detailed.sh`)
- [ ] Validate pipeline with synthetic data (100 samples)
- [ ] Train demo model (`demo_train.sh`)
- [ ] Test demo model (`test_demo_model.py`)
- [ ] **Collect real dawn images (500+ per class)** — awaiting hardware
- [ ] Train production model on real data
- [ ] Calibrate thresholds for Palestine latitude (~31.5°N)
- [ ] Live camera testing (3–6 AM)
- [ ] Systemd service for auto-start at boot

## ⏳ Future (Phase 3: Enhancement)
- [ ] Multi-location support (different lat/long thresholds)
- [ ] ONNX/TFLite conversion for edge devices
- [ ] OpenClaw skill integration (expose as service)
- [ ] Web dashboard for monitoring predictions
- [ ] Historical log viewer
- [ ] Multi-camera support (redundancy)
- [ ] Cloud model update mechanism
- [ ] Audio adhan playback (optional)

## 🐛 Known Issues
- Demo mode requires numpy (not available in current environment) — will work on Pi after install
- `main.py` rule-based fallback still imports cv2 at top level — needs same conditional treatment
- Synthetic images quality is low (geometric shapes) — for logic testing only

## 📅 Target Dates
- Pi deployment start: 2026-04-21 (tomorrow) — pending hardware availability
- Real image collection: 3–5 days minimum (weather dependent)
- Production model training: after dataset ready
- Full system operational: ~1 week from Pi setup
