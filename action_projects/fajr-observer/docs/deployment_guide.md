# Deployment Guide — Fajr Observer Agent

## Hardware Requirements

- **Raspberry Pi 3B+ or newer** (or any Linux PC)
- **Camera:** Raspberry Pi Camera v2/v3 or USB webcam (≥1080p)
- **Power supply** (stable)
- **Optional:** Speaker/headphone jack for Adhan audio

---

## Software Setup (Raspberry Pi)

### Step 1: OS Installation
1. Download **Raspberry Pi OS Lite** (no desktop needed)
2. Flash to SD card using Raspberry Pi Imager
3. Enable SSH and set locale (en_US.UTF-8)

### Step 2: Initial System Config
```bash
sudo raspi-config
  → System Options → Hostname: "fajr-observer"
  → Interface Options → Camera: Enable
  → Interface Options → SSH: Enable
  → Localisation → Timezone: Asia/Gaza (or your zone)
  → Reboot
```

### Step 3: Install Dependencies
```bash
cd /home/pi
git clone <your-repo> fajr-observer
cd fajr-observer
scripts/install.sh
```

**Manual install if script fails:**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libopencv-dev ffmpeg mpv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Camera Mounting
- Mount camera **facing due east** (use compass)
- Ensure **no obstructions** (trees, buildings) in lower 15° of sky
- Adjust tilt: horizon should be at ~2/3 height in frame
- Secure with waterproof housing if outdoors

### Step 5: Configuration
Edit `config/thresholds.json`:
```json
{
  "global": {
    "capture_interval_seconds": 15,
    "min_confidence": 0.92
  },
  "latitudinal_zones": {
    "tropical": {"lat_range": [-23.5, 23.5], ...}
    // set lat_range that includes your latitude
  }
}
```

Set your exact latitude/longitude in `src/decision/fajr_engine.py` or via CLI args.

### Step 6: Adhan Audio
Place an MP3 file at `data/azan_fajr.mp3`.  
Recommended: clear, high-quality Adhan (no music).  
Or leave empty — only Telegram notifications will work.

### Step 7: Test Run
```bash
# Dry-run first (no Adhan)
./scripts/run_observer.sh --dry-run --lat 21.5 --lon 39.0

# Live (will play audio if present)
./scripts/run_observer.sh --live --lat 21.5 --lon 39.0
```

You should see console output per frame:
```
[04:15:22] NIGHT | conf=0.98 | hits=1
[04:15:37] FALSE_DAWN | conf=0.75 | hits=1
[04:15:52] FALSE_DAWN | conf=0.80 | hits=2
[04:16:07] TRUE_DAWN | conf=0.88 | hits=1  ← first hit
[04:16:22] TRUE_DAWN | conf=0.91 | hits=2  ← second
[04:16:37] TRUE_DAWN | conf=0.93 | hits=3  ← third → TRIGGER
🕌 ADHAN TRIGGER at 2024-06-15 04:16:37
```

Images saved to `logs/images/` for verification.

---

## Calibration

### Fine-tuning Thresholds
If false positives occur:
1. Check saved images — what does your false dawn look like?
2. Adjust `config/thresholds.json`:
   - Increase `horizontal_spread_min` if Classifier triggers too early
   - Decrease `intensity_min` if it never triggers
3. Re-run test

### Multi-day Validation
- Run for 7 consecutive days
- Compare detected true dawn times with local mosque Adhan
- Note discrepancies and adjust thresholds accordingly

---

## Production Deployment

### As Systemd Service (auto-start at boot)
Create `/etc/systemd/system/fajr-observer.service`:
```ini
[Unit]
Description=Fajr Observer Agent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/fajr-observer
Environment="PATH=/home/pi/fajr-observer/venv/bin"
ExecStart=/home/pi/fajr-observer/scripts/run_observer.sh --live --lat 21.5 --lon 39.0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable fajr-observer
sudo systemctl start fajr-observer
sudo systemctl status fajr-observer  # verify
```

### Log Rotation
`logs/fajr-*.log` are daily; use `logrotate` if disk space is limited.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| Never triggers | Thresholds too high | Lower `horizontal_spread_min` |
| Triggers too early | False dawn classified as true | Increase `vertical_streak_max` |
| Camera not found | Wrong device ID | Set `device_id: 0` or 1 in `camera_settings.yaml` |
| No audio | Missing player | Install `mpv`: `sudo apt install mpv` |
| High CPU | No GPU acceleration | Use lower resolution (1280×720) |

---

## Safety & Ethics

- **No recording of people** — camera faces sky only
- **Local processing** — no cloud uploads
- **Human override** — dry-run mode, easy to disable
- **Transparent logs** — anyone can audit decisions

---

**"And the dawn when it breathes"** (Quran 81:18) — let the agent help you witness it.
