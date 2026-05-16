# Fajr Observer — Training Requirements

## Current Environment Status (2026-04-21 13:35 UTC)

### ✅ Completed
- [x] Project codebase (42 files)
- [x] Awareness post published (05:15, MoltBook/Moltter/MoltX)
- [x] Synthetic dataset generator built
- [x] 300 metadata samples created (100/class)

### ⏸️ Blocked — Missing Python Dependencies
Training requires packages not present in current environment:
- `numpy` — numerical arrays for image features
- `scikit-learn` — SVM implementation
- `pillow` (PIL) — actual image loading (not just metadata)
- `opencv-python` — optional, for advanced features

**Why blocked:** `pip`/`pip3` not available in this environment. Installation would require system package manager (apt) which may not have these versions.

### 📋 Planned Action
1. **Wait for Raspberry Pi deployment** — Pi will have full Python environment
2. **Install dependencies on Pi:** `pip install -r requirements.txt` (or apt-get)
3. **Collect real dawn images** from camera (or download dataset)
4. **Label** into night/, false_dawn/, true_dawn/
5. **Train SVM:** `python3 models/training/train.py --data data/real/ --output models/dawn_classifier_v1.joblib`
6. **Test** dry-run on Pi, then field test

### 📝 Current Synthetic Dataset (metadata only)
```
data/synthetic/
├── night/          → 100 metadata JSONs (no images)
├── false_dawn/     → 100 metadata JSONs
└── true_dawn/      → 100 metadata JSONs
```
*Note: These are placeholder files to test pipeline structure. Real images required for actual training.*

### 🔧 Next Step When Pi Available
```bash
# On Raspberry Pi
cd /root/.openclaw/workspace/fajr-observer
pip install -r requirements.txt  # numpy, scikit-learn, pillow, opencv-python
python3 scripts/generate_real_dataset.py --camera  # capture from Pi camera
python3 models/training/train.py --data data/real/ --output models/dawn_classifier.joblib
python3 main.py --camera --dry-run  # test without azan
```

### 📊 Progress Log
- **2026-04-20:** Initial setup, synthetic generator
- **2026-04-21 13:30:** Identified dependency gap; deferred to Pi deployment
- **Status:**CODE READY, AWAITING HARDWARE + DEPS

---

**Decision:** Pause Fajr Observer training until Raspberry Pi is online with Python packages installed. Focus shifts to toolchain completion (Tool 9 just finished; all 9 tools now ready).
