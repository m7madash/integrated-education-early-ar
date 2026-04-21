# Fajr Observer — Complete Raspberry Pi Deployment

**Goal:** Run fully automated on Raspberry Pi with one command.

---

## 📦 **Prerequisites on Raspberry Pi**

- Raspberry Pi OS (Bullseye or later)
- Raspberry Pi Camera Module connected
- Internet access (for initial package download)
- SSH or console access

---

## 🚀 **Quick Start (3 Commands)**

```bash
# 1. Clone repository (if not already)
git clone https://github.com/m7madash/Abduallh-projects.git
cd Abduallh-projects/fajr-observer

# 2. Make scripts executable
chmod +x scripts/setup_pi.sh scripts/auto_pipeline.sh

# 3. Run full pipeline (installs deps, trains, tests)
bash scripts/auto_pipeline.sh
```

**That's it!**  
The script will:
1. Install system packages (Python3, pip)
2. Create venv and install numpy, scikit-learn, pillow, opencv-python
3. Generate synthetic training data (until real camera available)
4. Train SVM model (`models/dawn_classifier.joblib`)
5. Dry-run test without camera
6. Print next steps

---

## 📁 **File Structure After Setup**

```
fajr-observer/
├── venv/                    # Python virtual environment
├── data/
│   ├── real/               # Training images (synthetic initially)
│   └── synthetic/          # Generated dataset
├── models/
│   └── dawn_classifier.joblib  # Trained model
├── logs/                   # Training & runtime logs
├── scripts/
│   ├── setup_pi.sh         # Dependency installer
│   ├── auto_pipeline.sh    # Full automated pipeline
│   ├── generate_synthetic_dataset.py
│   ├── run_demo.sh
│   └── train.py
└── main.py                 # Main observer (camera + inference)
```

---

## 🔧 **Manual Steps (if needed)**

### **Install dependencies only**
```bash
bash scripts/setup_pi.sh
```

### **Generate dataset only**
```bash
source venv/bin/activate
python3 scripts/generate_synthetic_dataset.py --samples 1000 --output data/real/
```

### **Train only**
```bash
source venv/bin/activate
python3 models/training/train.py --data data/real/ --output models/dawn_classifier.joblib
```

### **Run with camera**
```bash
source venv/bin/activate
python3 main.py --camera
```

---

## ⚙️ **Configuration**

Edit `config/camera_settings.yaml` for:
- Camera resolution
- Frame rate
- Detection thresholds

Edit `config/thresholds.json` for:
- Dawn probability thresholds
- False dawn filtering
- Confidence cutoffs

---

## 📊 **Monitoring & Logs**

- Training logs: `logs/training_*.log`
- Runtime logs: `logs/fajr_observer_*.log`
- Model metrics: printed after training (accuracy, precision, recall)

---

## 🐛 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| `ImportError: No module named numpy` | Run `scripts/setup_pi.sh` again |
| Camera not detected | Check `raspistill` works, ensure camera enabled in `raspi-config` |
| Low accuracy | Increase synthetic samples (`--samples 5000`), then retrain |
| High false positives | Adjust thresholds in `config/thresholds.json` |

---

## 📈 **Expected Performance**

- **Training time:** ~5–10 minutes on Pi 4 (1000 samples)
- **Inference time:** < 0.1s per frame
- **Accuracy target:** >90% on balanced dataset

---

## 🔐 **Islamic Ethics Note**

This tool is designed to help Muslims perform Fajr prayer on time.  
It does not store personal data. Camera feed is processed locally only.

---

**Ready for deployment.** One command: `bash scripts/auto_pipeline.sh`
