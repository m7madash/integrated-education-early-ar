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

## 💡 Solutions (شاملة، متعددة المستويات)

### ✅ Level 1: Individual Protection (فوري)
- [x] دليل: "كيفية إعادة تعيين Ad ID" (عربي/انجليزي)
- [x] Browser extensions (uBlock Origin, Privacy Badger, DuckDuckGo)
- [ ] App permission auditor (scan Android apps for location)
- [ ] Firefox Focus / Tor for mobile
- [ ] Bulk remove ad permissions script (Android)

### ✅ Level 2: Agent Tools (تقني — قيد البناء)
- [x] **CLI basic** (`src/privacy_shield/cli.py`) — demo works
- [ ] **AdBlocker Rule Generator** — filters for webloc domains
- [ ] **MAID Rotator** — auto-randomize advertising IDs
- [ ] **Location Spoofer** (for privacy protection only)
- [ ] **SDK Scanner** — detect surveillance SDKs in apps
- [ ] **Network Monitor** — alert on RTB requests

### ✅ Level 3: Legal & Advocacy
- [x] advocacy/ folder (letters to Congress)
- [ ] Automated letter generator for Fourth Amendment Is Not For Sale Act

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
