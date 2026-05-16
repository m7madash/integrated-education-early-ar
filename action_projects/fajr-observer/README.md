# Fajr Observer Agent — determines TRUE DAWN (الفجر الصادق) via camera + AI

**Problem:** Traditional prayer times rely on astronomical calculations that approximate dawn (الفجر الكاذب).  
**Solution:** Computer vision + machine learning to visually detect the transition from false dawn to true dawn — exactly as the Salaf did by looking at the horizon.

---

## 🎯 What It Does

- **Captures** images of the eastern sky every 10–30 seconds before Fajr (3:00–6:00 AM)
- **Analyzes** light distribution (vertical streak vs horizontal glow)
- **Classifies** current state: Night | False Dawn (الكاذب) | True Dawn (الصادق)
- **Triggers** the Adhan automatically when true dawn is confirmed (with human override)
- **Logs** all observations for later verification and model improvement

---

## 🔬 The Science (INAUGURAL)

### False Dawn (الفجر الكاذب):
- **Shape:** Vertical column, like a wolf's tail (ذيل السرحان)
- **Orientation:** Longitudinal (طولي) in the sky
- **Duration:** 15–30 minutes, then disappears
- **Halal Status:** Does NOT permit Fajr prayer, does NOT prohibit Suhoor

### True Dawn (الفجر الصادق):
- **Shape:** Horizontal spread across the entire eastern horizon
- **Orientation:** Latitudinal (عرضي), touches the horizon
- **Duration:** Increases until sunrise
- **Halal Status:** Permits Fajr prayer, prohibits Suhoor

**Hadith (Sahih):** "الْفَجْرُ فَجْرَانِ: فَجْرٌ يُ潜意识ِينَ الصَّلاَةَ وَلاَ يُحَرِّمُ الطَّعَامَ، وَفَجْرٌ يُحَرِّمُ الطَّعَامَ وَيُحِلُّ الصَّلاَةَ"  
— Al-Albani, *Sahih al-Jami`* 2031

---

## 📁 Project Structure

```
fajr-observer/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── config/
│   ├── thresholds.json         # Light thresholds per latitude/season
│   └── camera_settings.yaml    # Camera parameters (exposure, interval)
├── src/
│   ├── camera/
│   │   ├── capture.py          # Take pictures every N seconds
│   │   └── calibration.py       # Adjust exposure, white balance
│   ├── detection/
│   │   ├── dawn_classifier.py  # ML model: classify image state
│   │   ├── features.py         # Extract optical features (spread, intensity)
│   │   └── thresholds.py       # Convert solar angle → expected brightness
│   ├── decision/
│   │   ├── fajr_engine.py      # Decision logic: multiple confirmations
│   │   └── validator.py        # Check for false positives (clouds, lights)
│   ├── notification/
│   │   ├── azan_trigger.py     # Play Adhan sound, send Telegram alert
│   │   └── logger.py           # Save image + timestamp + decision
│   └── utils/
│       ├── geo.py              # Location → sunrise/fajr times (astral)
│       └── sun_position.py     # Solar elevation angle calculator
├── models/
│   ├── dawn_classifier_v1.h5   # Trained CNN (Keras/TFLite)
│   └── training/
│       ├── dataset/            # Labeled images (night/false/true)
│       └── train.py            # Training script
├── tests/
│   ├── test_capture.py
│   ├── test_classifier.py
│   └── test_integration.py
├── docs/
│   ├── fajr_science.md         # Optical physics of dawn
│   ├── hadith_collection.md    # relevant ahadith
│   └── deployment_guide.md     # RPi setup
├── scripts/
│   ├── install.sh              # `apt-get install` + pip install
│   ├── run_observer.sh         # Start service
│   └── collect_dataset.sh      # Bulk download images for training
└── LICENSE                     # MIT (halal use only)
```

---

## 🚀 Quick Start (Developer)

```bash
# 1. Clone + install
git clone <repo> fajr-observer
cd fajr-observer
scripts/install.sh

# 2. Configure location (lat, lon, timezone)
cp config/thresholds.example.json config/thresholds.json
# Edit with your coordinates

# 3. Run in test mode (simulated images)
python3 -m src.decision.fajr_engine --test

# 4. Connect camera, start live
python3 -m src.camera.capture --live
```

---

## ⚖️ Safety & Ethics

- ✅ No surveillance of people (sky only)
- ✅ All processing local (no cloud upload)
- ✅ Human override required for Adhan (configurable)
- ✅ Transparent logs (anyone can verify)
- ✅ Does NOT replace human Muazzin — assists him

---

## 📊 Output Example

```json
{
  "timestamp": "2026-04-20T04:23:12",
  "location": "Gaza, Palestine",
  "solar_elevation": -18.2,
  "classification": "true_dawn",
  "confidence": 0.98,
  "image_saved": "logs/2026-04-20_042312.jpg",
  "action": "trigger_adhan"
}
```

---

## 🤝 Contributing

- **Dataset:** Submit labeled dawn images (night/false/true) to `models/training/dataset/`
- **Code:** PRs welcome — keep logic simple, well-commented
- **Deployment:** Share your RPi/camera setup details in `docs/deployment_guide.md`

---

**"And by the sky and its construction... and the dawn when it breathes"** (Quran 81:18–20)

*This agent sees what eyes have always seen — but now it can tell us exactly when.*
