# Deepfake Detection Models (Placeholder)

Place your pretrained models here.

For v0.1.0, we use heuristics only (no ML models). For v0.2.0+, integrate:

- **Image Forensics Model**: CNN trained on manipulated vs authentic images
  - Suggested: `models/efficientnet_forensics.pth`
  - Datasets: CASIA, Columbia, NIST16

- **Video Deepfake Model**: 3D-CNN or Two-Stream network
  - Suggested: `models/xception_deepfake.pth`
  - Datasets: FaceForensics++, DFDC

- **Audio Deepfake Model**: Wav2Vec2-based synthetic voice detector
  - Suggested: `models/audio_deepfake.pt`
  - Datasets: ASVspoof, FakeOrReal

To add a model:
1. Download weights from trusted source
2. Place in this directory
3. Update `video.py` or `image.py` to load and use

⚠️ Never download models from untrusted sources (they may contain backdoors).

🕌 Always verify the integrity of any third-party model before use.
