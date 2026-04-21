# Privacy Shield — Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] — 2026-04-21 (Initial Release)

### Added
- **crypto.py**: Fernet-based file encryption/decryption (AES-128-CBC + HMAC-SHA256)
  - Password-derived key via PBKDF2 (100k iterations)
  - Salt stored with ciphertext for stateless decryption
- **breach.py**: HaveIBeenPwned API v3 integration
  - Email breach checking with local caching (10 min TTL)
  - Phone lookup support (requires API key)
- **browser.py**: Browser hardening generators
  - Firefox: prefs.js with fingerprinting resistance, WebRTC disable, telemetry off
  - Chrome: enterprise policies JSON (Incognito mode, autofill disabled, etc.)
- **vpn.py**: Public IP detection and VPN status checker
  - Compares against baseline IP to detect VPN activation
  - Recommends ethical VPN providers (Mullvad, ProtonVPN, IVPN)
- **tests/test_privacy.py**: core functionality tests
- **requirements.txt**: dependencies (cryptography, requests)
- **Full README** with installation and usage examples

### Technical Notes
- All crypto operations use `cryptography` library (fernet)
- No data leaves the device except HIBP API calls (optional)
- Supports Python 3.8+
- Caching layer respects rate limits

---

## [Planned] — Future Releases

### [0.2.0] — Enhanced Privacy
- Android app permission scanner
- MAID (Mobile Advertising ID) rotator
- RTB domain blocker generation (simple_rtb_blocker.py → production)
- Location spoofer (ethical use only)

### [0.3.0] — Education & Scale
- Arabic guide: "الخصوصية للجميع"
- Video script & infographic
- Weekly breach alert newsletter (email)
- Partnership with digital rights orgs (EFF, Access Now)

### [1.0.0] — Full Suite
- GUI desktop app (Tkinter/PyQt)
- Browser extension (Chrome/Firefox add-on)
- Mobile app (Flutter)
- Docker image for easy deployment

---

**Ethical Boundary**: This tool protects privacy — it does not enable illegal activities.  
No backdoors, no data collection, fully auditable open source.
