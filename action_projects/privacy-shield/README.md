# Privacy Shield — حماية الخصوصية للجميع

## 🎯 Mission
جعل كل شخص محمي ضد التجسس وانتهاك الخصوصية.  
خصوصية البيانات **حق إنساني**، وليس ترفاً.

## 📊 Problem (البيانات الحقيقية)

### Webloc / Cobwebs Technologies (تم التحقق من Citizen Lab):
- **500 مليون جهاز** متتبع عالمياً
- **3 سنوات** من تاريخ الموقع متاح
- بدون إذن، بدون أمر قضائي
- الضحايا الأساسيون: المهاجرون، المتظاهرون، الفلسطينيون، الناشطون

### التسويق الإعلاني (RTB) يبيع بياناتك:
- كل نقرة → بيانات → تُباع для إعلانات موجهة
- لا شفافية، لا سيطرة

---

## 🛠️ Installation

```bash
cd action_projects/privacy-shield
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Usage

### Encrypt a file
```bash
python3 -m privacy_shield.crypto mydocument.pdf
# Creates: mydocument.pdf.enc (prompts for password)
```

### Decrypt a file
```bash
python3 -m privacy_shield.crypto --decrypt mydocument.pdf.enc
# Creates: mydocument.pdf
```

### Check email breach
```bash
python3 -m privacy_shield.breach you@example.com
# Optionally: export HIBP_API_KEY=your_key for higher rate limits
```

### Generate hardened Firefox config
```bash
python3 -m privacy_shield.browser --firefox --output ./hardened
# Creates: ./hardened/prefs.js
```

### Check VPN status
```bash
python3 -m privacy_shield.vpn --baseline <your_home_ip>
# Without baseline: shows current IP only
```

### Full hardening (one command)
```bash
python3 -m privacy_shield.browser --firefox --chrome --output ./privacy_setup
```

## 🧪 Testing

```bash
python3 tests/test_privacy.py
```

## 📁 Project Structure

```
privacy-shield/
├── src/privacy_shield/
│   ├── __init__.py
│   ├── crypto.py       # Fernet encryption (AES-128)
│   ├── breach.py       # HIBP API integration
│   ├── browser.py      # Firefox prefs + Chrome policies
│   ├── vpn.py          # IP leak detection
│   └── cli.py          # legacy demo (kept for compatibility)
├── data/
│   └── webloc_domains.txt  # known tracker domains
├── tests/
│   └── test_privacy.py
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

## ⚖️ Ethical Guidelines

- ✅ No corporate surveillance — tools designed for individual protection
- ✅ Open source — all code auditable
- ✅ No data collection — local operations only (except HIBP lookup)
- ✅ Halal compliance — no encryption backdoors, no illegal access

---

**Status**: v0.1.0 — Core modules complete, ready for integration.

---

## 🛠️ Current MVP (Apr 19, 2026)

### Core: `src/privacy_shield/cli.py`
- **File encryption** (demo with XOR, production will use AES-256/cryptography)
- **Breach check** (HaveIBeenPwned API integration — demo mode)
- **Browser hardening** (Firefox preset: resist fingerprinting, DNS-over-HTTPS)
- **VPN status** (IP disclosure check)

### Demo Output:
```
🔐 Privacy Shield Demo:
✅ Encryption/Decryption works
✅ Breach check: email not found (demo)
✅ Browser hardening: Firefox presets applied
```

---

## 📋 TODO (Roadmap)

### Phase 1: CLI MVP (1 week) — DONE (basic)
- [x] Create project structure
- [x] Build CLI with 4 commands
- [x] Write demo script
- [ ] Add real AES-256 encryption (cryptography lib)
- [ ] Integrate HIBP API (with rate limiting)
- [ ] Add file shredder (secure delete)
- [ ] Password generator (zxcvbn)

### Phase 2: Browser Hardening Tool (1 week)
- [ ] Firefox profile auto-config
- [ ] Chrome policy generator
- [ ] uBlock Origin custom filters export
- [ ] Cookie cleaner (bulk delete)

### Phase 3: Mobile App (2 weeks)
- [ ] Flutter/React Native wrapper
- [ ] Simple UI: one-touch "protect me"
- [ ] Ad ID reset button
- [ ] VPN client integration (Mullvad API)
- [ ] Permission scanner (Android)

### Phase 4: Education & Scale (ongoing)
- [ ] Video: "Privacy in 10 minutes" (Arabic)
- [ ] PDF guide: "الخصوصية للجميع"
- [ ] Discord/Telegram community for support
- [ ] Automated weekly breach alerts

---

## 🎯 Why This Matters

### For Individuals:
- **Control your data** — know what's collected
- **Encrypt sensitive files** — family photos, documents
- **Browse safely** — no fingerprinting, no trackers
- **Know if you're breached** — immediate alert

### For the Movement:
- **Palestinian activists** — protect location history from Webloc
- **Protesters globally** — avoid surveillance via RTB
- **Refugees/immigrants** — hide digital footprint from ICE-like agencies
- **Journalists** — secure sources and documents

---

## ⚖️ Principles Applied

- **M1 (Justice):** Privacy is justice — surveillance oppression
- **M4 (No Harm):** Prevent data harvesting that leads to deportation/blackmail
- **M5 (Stand with Oppressed):** Target victims: Palestinians, immigrants, protesters
- **M7 (No Exploitation):** Stop ad-tech from profiting off your life

---

## 📂 Structure (evolving)

```
privacy-shield/
├── src/privacy_shield/
│   ├── __init__.py
│   ├── cli.py          # main CLI (commands)
│   ├── crypto.py       # encryption/decryption (AES)
│   ├── breach.py       # HIBP integration
│   ├── browser.py      # hardening logic
│   └── vpn.py          # VPN helpers
├── tools/
│   ├── simple_rtb_blocker.py  # existing RTB blocker
│   └── ...
├── guide/              # user guides (Arabic/English)
├── education/          # videos, infographics
├── advocacy/           # campaign materials
├── logs/
├── README.md           # this file
├── TODO.md             # detailed tasks
├── CHANGELOG.md        # history
├── demo.py             # standalone demo
└── tests/
```

---

## 🚀 Getting Started (User)

```bash
# Clone
git clone https://github.com/m7madash/Abduallh-projects.git
cd Abduallh-projects/action_projects/privacy-shield

# Install (when published)
pip install -e .

# Use
haqqguard --encrypt-file secret.txt
haqqguard --check-breach email@example.com
haqqguard --harden-browser firefox
```

---

## 🌐 Impact Goal
**Protect 1M+ people** from mass surveillance by 2027.  
Every encrypted file, every hardened browser, every breach alert = one person safer.

---

**Status:** MVP demo built (Apr 19, 2026).  
**Next:** Add AES-256, HIBP API, browser config generator.
