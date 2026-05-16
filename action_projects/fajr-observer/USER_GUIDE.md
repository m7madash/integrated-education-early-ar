# Fajr Observer — User Guide

## Quick Start (5分钟)

### Step 1: Install Dependencies
```bash
cd fajr-observer
./scripts/install_detailed.sh
```
*This installs OpenCV, Python packages, and media players.*

### Step 2: Configure Location
Edit `config/thresholds.json` if needed (auto-detects most latitudes).  
Or set via command line (see Step 4).

### Step 3: Connect Camera
- USB webcam or Raspberry Pi Camera
- Face **due east** (use compass)
- Horizon should be visible in lower 20% of frame

### Step 4: Test Run (Dry)
```bash
./scripts/run_observer.sh --dry-run --lat 21.5 --lon 39.0
```
You should see:
```
[04:15:22] NIGHT | conf=0.98 | hits=1
[04:15:37] FALSE_DAWN | conf=0.75 | hits=1
...
```
**No Adhan sound** in dry-run.

### Step 5: Live Run
```bash
./scripts/run_observer.sh --live --lat 21.5 --lon 39.0
```
When TRUE_DAWN is confirmed:
- Adhan MP3 plays (if `data/azan_fajr.mp3` exists)
- Telegram notification sent (if bot token configured)
- Image saved to `logs/images/`

---

## Configuration

### Latitude & Timezone
Set in `scripts/run_observer.sh` or pass CLI args:
```bash
python3 main.py --lat 21.5 --lon 39.0 --tz Asia/Gaza --dry-run
```

### Threshold Tweaking
If false positives:
1. Check captured images in `logs/images/`
2. Edit `config/thresholds.json`:
   - Increase `"horizontal_spread_min"` to delay trigger
   - Decrease `"intensity_min"` if never triggers
3. Re-test

### Camera Settings
Edit `config/camera_settings.yaml`:
```yaml
device_id: 0          # change to 1 if USB cam
width: 1920
height: 1080
exposure: -1          # -1 = auto, or set manual (0-100)
iso: 400
interval_seconds: 15  # capture every 15s
```

---

## Daily Operation

### Automated (systemd)
```bash
sudo cp scripts/fajr-observer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fajr-observer
sudo systemctl start fajr-observer
sudo systemctl status fajr-observer
```

### Logs
- Daily logs: `logs/fajr_YYYY-MM-DD.log`
- Images: `logs/images/` (auto-rotated after 30 days)

---

## Training Your Own Model

After collecting ~500 images per class:

```bash
# Label your images into:
#   models/training/dataset/night/
#   models/training/dataset/false_dawn/
#   models/training/dataset/true_dawn/

python3 models/training/train.py --data models/training/dataset --model svm --output models/dawn_classifier_v1.joblib
```

Then update `dawn_classifier.py` to load the trained model instead of rules.

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| No camera | `ls /dev/video*` — does `/dev/video0` exist? |
| No trigger | Thresholds too high? Lower `horizontal_spread_min` in thresholds.json |
| False trigger | Moon present? Increase `consecutive_hits` to 4 or 5 |
| Audio not playing | `mpv --really-quiet data/azan_fajr.mp3` test manually |
| High CPU | Reduce image resolution in `camera_settings.yaml` |

---

## Safety & Ethics

- **Sky-only:** Camera must face sky only (no people/private property)
- **Local only:** All processing on-device (no cloud)
- **Human override:** `--dry-run` mode; can stop anytime
- **Audit trail:** All decisions logged with images

---

**"So observe the sky, and read the signs."** — Fajr Observer principle
