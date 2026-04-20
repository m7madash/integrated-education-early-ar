# Fajr Observer — Raspberry Pi Deployment Checklist

> **Target:** Raspberry Pi (any model with camera support)
> **Goal:** Detect true dawn (الفجر الصادق) and trigger adhan/notification

---

## ✅ Phase 0: Pre-Deployment (Before Touching Pi)

- [x] Code complete (42 files) — commit `73614bd7`
- [x] `install_detailed.sh` created — installs OpenCV, PIL, numpy, sklearn
- [x] `Dockerfile` created (alternative container deployment)
- [x] `USER_GUIDE.md` updated with --demo mode
- [x] `deployment_guide.md` written
- [x] `PROJECT_SUMMARY.md` updated
- [x] GitHub pushed (m7mad-ai-work) — sync complete
- [x] `train.py` conditional cv2 import tested
- [ ] **Decision**: Use Pi OS Lite or Desktop? (Lite recommended for headless)
- [ ] **Decision**: Camera type: Raspberry Pi Camera Module (CSI) أو USB webcam?

---

## 📦 Phase 1: Raspberry Pi Setup

### 1.1 Raspberry Pi OS
- [ ] Flash Raspberry Pi OS Lite (64-bit) using Raspberry Pi Imager
- [ ] Enable SSH before first boot (create `ssh` file in boot partition)
- [ ] Set hostname: `fajr-observer` (optional)
- [ ] Configure WiFi (create `wpa_supplicant.conf` in boot partition) OR use Ethernet
- [ ] First boot — wait 2–5 min for initialization
- [ ] `ssh pi@<ip>` — default password `raspberry`
- [ ] Change default password: `passwd`

### 1.2 System Update
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 1.3 Camera Enable
```bash
sudo raspi-config
# → Interface Options → Camera → Enable
# → Would you like to enable? → Yes
sudo reboot
```
**Verify camera works:**
```bash
sudo apt install -y raspberrypi-ui-mods  # includes camera preview
# OR test via command line:
sudo apt install -y ffmpeg
ffmpeg -f v4l2 -i /dev/video0 -t 1 test.jpg  # should capture 1 frame
```

---

## 🛠️ Phase 2: Project Deployment

### 2.1 Clone Repository
```bash
cd ~
git clone https://github.com/m7madash/m7mad-ai-work.git
cd m7mad-ai-work/fajr-observer
```

### 2.2 Install Dependencies (Recommended: use provided script)
```bash
bash scripts/install_detailed.sh
```
**What it does:**
- Installs system libs: `libopencv-dev`, `libjpeg-dev`, `libpng-dev`, `libavcodec-dev`
- Upgrades pip
- Installs Python packages: `opencv-python-headless`, `pillow`, `numpy`, `scikit-learn`, `joblib`

**Manual alternative:**
```bash
sudo apt install -y python3-opencv python3-pil python3-numpy python3-sklearn python3-joblib
```

### 2.3 Verify Python Environment
```bash
python3 -c "import cv2; print('cv2:', cv2.__version__)"
python3 -c "import PIL; print('PIL:', PIL.__version__)"
python3 -c "import numpy; print('numpy:', numpy.__version__)"
python3 -c "import sklearn; print('sklearn:', sklearn.__version__)"
```
All should print versions without errors.

---

## 🧪 Phase 3: Pipeline Validation (Demo)

### 3.1 Generate Synthetic Dataset (Lightweight)
```bash
python3 scripts/generate_synthetic_dataset.py --samples 100 --output models/training/dataset
# Creates: models/training/dataset/{night,false_dawn,true_dawn}/
# Each folder: 100 PNG images + JSON metadata
```

### 3.2 Train Demo Model
```bash
bash scripts/demo_train.sh
# Output: models/dawn_classifier_demo.joblib
# Time: ~10–30 seconds (synthetic data)
```

### 3.3 Validate Demo Model
```bash
python3 scripts/test_demo_model.py
# Expected: ✅ Demo model works correctly — recognized synthetic true dawn
```

### 3.4 Test Rule-Based Fallback (No camera needed)
```bash
python3 main.py --model models/dawn_classifier_demo.joblib --mode rule-based
# Should output: "Rule-based classification: [CLASS]" with mock image analysis
```

**If all above succeed → pipeline is functional.**

---

## 📸 Phase 4: Real Image Collection

### 4.1 Camera Setup
- [ ] Connect Raspberry Pi Camera Module to CSI port OR plug USB webcam
- [ ] Test live preview:
  ```bash
  # For CSI camera:
  libcamera-jpeg -o test.jpg --width 640 --height 480
  # For USB:
  fswebcam -r 640x480 test.jpg
  ```
- [ ] Verify image saved and viewable

### 4.2 Capture Protocol (3:00–6:00 AM local time)
- [ ] Create capture script (use `scripts/collect_dataset.sh` as template)
- [ ] Set up cron to auto-capture every 10 minutes during dawn window:
  ```bash
  crontab -e
  # Add:
  */10 3-5 * * * /home/pi/fajr-env/bin/python3 /home/pi/m7mad-ai-work/fajr-observer/scripts/capture_training.py --output models/training/dataset
  ```
- [ ] Manually verify first batch of images (look at horizon, lighting)
- [ ] Label each image: does it show night / false dawn / true dawn?

### 4.3 Dataset Structure
```
models/training/dataset/
├── night/
│   ├── gaza_20260421_0320.jpg
│   └── ...
├── false_dawn/
│   ├── gaza_20260421_0345.jpg
│   └── ...
└── true_dawn/
    ├── gaza_20260421_0430.jpg
    └── ...
```

**Minimum:** 500 images per class (1,500 total)  
**Ideal:** 1,000+ per class (3,000 total) for robust model

### 4.4 Dataset Quality Check
```bash
# Count images
find models/training/dataset -name "*.jpg" | wc -l
# Should be >= 1500

# Quick visual spot-check (first 5 of each class)
ls models/training/dataset/night/ | head -5 | xargs -I{} display models/training/dataset/night/{} 2>/dev/null
```

---

## 🤖 Phase 5: Model Training (Production)

```bash
python3 models/training/train.py \
  --data models/training/dataset \
  --model svm \
  --output models/dawn_classifier_v1.joblib
```

**Expected output:**
```
=== Fajr Classifier Training ===
Total samples: 1500
Features: 9
  night: 500
  false_dawn: 500
  true_dawn: 500
Train: 1200, Test: 300
Training svm...
✅ Test accuracy: 92.3%
Model saved to: models/dawn_classifier_v1.joblib
```

**If accuracy < 80%:** collect more data, retrain.

---

## ⚙️ Phase 6: Threshold Calibration

Edit `config/thresholds.json` based on your latitude:

**For Palestine (Gaza) — Latitude ~31.5°N:**
```json
{
  "horizon_band_height": 0.15,
  "min_horizontal_spread": 0.45,
  "max_vertical_streak_ratio": 2.5,
  "min_brightness_for_true_dawn": 100,
  "max_brightness_for_false_dawn": 80
}
```

**How to calibrate:**
1. Run `main.py` live with camera
2. Note classifier output at known prayer times (check local mosque timeline)
3. Adjust thresholds until predictions align with observed dawn

---

## 🧪 Phase 7: Live Testing

```bash
python3 main.py \
  --model models/dawn_classifier_v1.joblib \
  --camera 0 \
  --notify telegram
```

**Expected behavior:**
- Camera opens, displays frame with overlay
- Every 30 seconds: analyze frame → predict class
- When `true_dawn` detected: send Telegram notification (configure `~/.openclaw/workspace/wallets/abdullah_wallet.json` or set `TELEGRAM_BOT_TOKEN`/`CHAT_ID`)
- Also trigger adhan audio (optional)

**Test window:** 3:00–6:00 AM local time (dawn period)

---

## ⚙️ Phase 8: Systemd Service (Auto-Start at Boot)

Create `/etc/systemd/system/fajr-observer.service`:

```ini
[Unit]
Description=Fajr Observer — True Dawn Detection
After=network.target camera.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/m7mad-ai-work/fajr-observer
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/pi/fajr-env/bin/python3 /home/pi/m7mad-ai-work/fajr-observer/main.py --model /home/pi/m7mad-ai-work/fajr-observer/models/dawn_classifier_v1.joblib --camera 0 --notify telegram
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start:
```bash
sudo cp scripts/fajr-observer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fajr-observer
sudo systemctl start fajr-observer
sudo systemctl status fajr-observer  # Verify running
```

**Logs:**
```bash
sudo journalctl -u fajr-observer -f  # follow
```

---

## 🔧 Phase 9: Calibration & Monitoring

### 9.1 Accuracy Tracking
- Log every prediction to `/var/log/fajr-observer/predictions.log`
- Review daily: `grep true_dawn predictions.log | wc -l` (should be 1 per day)
- If false positives: adjust thresholds

### 9.2 Telegram Notifications
Configure in `main.py` or env vars:
```bash
export TELEGRAM_BOT_TOKEN="123:abc"
export TELEGRAM_CHAT_ID="123456789"
```

### 9.3 Fallback Strategy
- If camera fails: use `--mode rule-based` as fallback
- Rule-based uses simple thresholding (horizon band, brightness)
- Less accurate but never fails completely

---

## 🐛 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `cv2 import error` | OpenCV not installed | Re-run `install_detailed.sh` |
| Camera not detected | CSI/USB not enabled | `sudo raspi-config` → Camera → Enable |
| No images captured | Wrong device path | Use `--camera /dev/video0` or `--camera 0` |
| Model accuracy low | Insufficient training data | Collect more images (aim for 1k/class) |
| False positives | Thresholds too loose | Increase `min_horizontal_spread` |
| Rate limit on API平台 | Too many posts | Reduce posting frequency; batch |

---

## 📊 Success Metrics

- ✅ **Detection accuracy** > 90% on test set
- ✅ **False positive rate** < 5% (one per week max)


- ✅ **True dawn notification** sent within 2 minutes of actual
- ✅ **System uptime** > 99% (auto-restart on failure)
- ✅ **Power consumption** < 5W (Pi Zero 2W recommended)

---

## 🎯 Next Steps After Deployment

1. **Monitor for 1 week** — log all predictions, manually verify
2. **Fine-tune thresholds** based on real-world performance
3. **Add multi-location support** (different lat/long configs)
4. **Package as Docker container** (already have Dockerfile)
5. **Publish as OpenClaw skill** — let other agents use it
6. **Community sharing** — post results on MoltBook (team: extremism-moderation? no, maybe new team: fajr-community)

---

**Last updated:** 2026-04-20 (completed code, awaiting Pi hardware)
**Maintainer:** Abdullah Haqq (KiloClaw)
