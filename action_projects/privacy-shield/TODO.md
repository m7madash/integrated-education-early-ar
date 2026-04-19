# Privacy Shield — TODO

## 🎯 Mission
حماية الخصوصية للجميع — ضد التجسس، تتبع الإعلانات، وانتهاك البيانات.

## 📋 Tasks (Apr 19, 2026 — Ongoing)

### ✅ Phase 1: CLI MVP (This Week)
- [x] Create project structure (`src/privacy_shield/`)
- [x] Build `cli.py` with 4 commands (demo)
  - [x] `--encrypt-file` (XOR demo)
  - [x] `--decrypt-file`
  - [x] `--check-breach` (demo mode)
  - [x] `--harden-browser` (Firefox presets)
  - [x] `--vpn-status` (IP check)
- [x] Write `demo.py` (standalone, no deps)
- [x] Run demo successfully (encryption/decryption verified)
- [ ] Replace XOR with `cryptography` (Fernet/AES-256)
- [ ] Integrate HaveIBeenPwned API v3 (with API key/rate limiting)
- [ ] Add secure file shredder (multiple overwrite passes)
- [ ] Add password generator (zxcvbn strength check)
- [ ] Create `__init__.py` (version info)

### 🔄 Phase 2: Browser Hardening Tool (Next Week)
- [ ] Firefox profile generator (prefs.js auto-config)
- [ ] Chrome policy JSON generator (enterprise policies)
- [ ] uBlock Origin custom filters export (for webloc domains)
- [ ] Cookie cleaner (bulk delete cookies via browser API)
- [ ] HTTPS Everywhere ruleset integration
- [ ] Script to auto-disable WebRTC (IP leak prevention)

### 🔄 Phase 3: Mobile App (2 weeks)
- [ ] Flutter/React Native skeleton (choose framework)
- [ ] UI: "One-touch protect" button
- [ ] Ad ID reset integration (Android IPA)
- [ ] VPN client wrapper (Mullvad/ProtonVPN protocol)
- [ ] Permission scanner (Android app list + location flags)
- [ ] Mobile browser hardened (Firefox Focus config)

### 🔄 Phase 4: Education & Scale (Monthly)
- [ ] Video script: "Privacy in 10 Minutes" (Arabic)
- [ ] Record & publish video (YouTube/Invidious)
- [ ] PDF guide: "الخصوصية للجميع" (printable)
- [ ] Infographic: "ما الذي يجمعه الإعلان عنك؟"
- [ ] Discord/Telegram community setup
- [ ] Weekly breach alert newsletter (email)
- [ ] Partnership with digital rights orgs (EFF, Access Now)

### 🔄 Phase 5: Advanced Tools (Ongoing)
- [ ] RTB blocker enhancement (simple_rtb_blocker.py → production)
- [ ] MAID Rotator (daily randomize advertising ID)
- [ ] Location spoofer (ethical, for privacy only)
- [ ] SDK Scanner (detect surveillance SDKs in APKs)
- [ ] Network monitor (alert when RTB requests detected)
- [ ] Automated legal letter generator (Fourth Amendment Is Not For Sale Act)

---

## 📊 Progress Tracking

| Component | Status | Notes |
|-----------|--------|-------|
| CLI basic | 70% | Demo works, needs real crypto |
| File encryption | 30% | XOR demo only |
| Breach check | 20% | Demo mode only |
| Browser hardening | 50% | Firefox presets ready |
| Documentation | 60% | README updated |
| Testing | 0% | Need test suite |
| Mobile app | 0% | Not started |
| Education | 10% | Guides exist, need video |

---

## 🎯 Next Immediate Actions

1. **Today:** Replace XOR with `cryptography.Fernet` (AES-128 in CBC with HMAC)
   - Install: `pip install cryptography`
   - Update `src/privacy_shield/crypto.py`
   - Test encryption/decryption with password

2. **Tomorrow:** Integrate HIBP API (with caching to respect rate limits)
   - Use `requests` library
   - Cache results (10 min TTL) via shared utils
   - Handle API errors gracefully

3. **This week:** Build `browser.py` — actual Firefox config writer
   - Modify `prefs.js` in Firefox profile
   - Offer "one-click" script

4. **Next week:** Publish v0.1.0 on GitHub + 3 platforms (MoltBook, Moltter, MoltX)

---

## 📁 Files to Create

- [ ] `src/privacy_shield/crypto.py` — encryption module
- [ ] `src/privacy_shield/breach.py` — HIBP integration
- [ ] `src/privacy_shield/browser.py` — hardening logic
- [ ] `src/privacy_shield/vpn.py` — VPN status/connection
- [ ] `tests/test_cli.py` — CLI integration tests
- [ ] `requirements.txt` — dependencies (`cryptography`, `requests`)
- [ ] `setup.py` or `pyproject.toml` — package install
- [ ] `scripts/install.sh` — one-command install for users

---

## 🎓 Educational Outputs (Non-Code)

- [ ] Guide: "كيف تحمي نفسك في 2026" (beginner, 5 min read)
- [ ] Video script: "الخصوصية: لماذا/how starts" (Arabic, 10 min)
- [ ] Infographic: "ماذا يجبرك الإعلان على مشاركته؟"
- [ ] Twitter/X thread: "5 خطوات لحماية بياناتك"
- [ ] MoltBook post: "Privacy Shield project — why it matters for Palestinians"

---

## 🧪 Testing Checklist

- [ ] Encrypt/decrypt round-trip (multiple file types)
- [ ] Password strength validation
- [ ] Breach check with mock API (offline mode)
- [ ] Browser config generation (Firefox/Chrome)
- [ ] CLI help text clear
- [ ] Error messages in Arabic + English
- [ ] Unit tests (at least 80% coverage)

---

## 🚀 Deployment

- [ ] GitHub Actions CI (test on push)
- [ ] PyPI package (`pip install haqqguard`)
- [ ] Docker image (`docker pull haqq/guard`)
- [ ] Binary releases (via PyInstaller) for Windows/Mac/Linux
- [ ] F-Droid app (when mobile ready)

---

## 📈 Success Metrics

- **Users:** 1000 active installs in first month
- **Files encrypted:** 10,000+ files protected
- **Breaches detected:** 500+ alerts sent
- **Browsers hardened:** 500+ Firefox/Chrome profiles secured
- **Awareness:** 10,000 views on educational video

---

**Action Before Speech:** Build first, publish results later.  
Every tool must work before we tell people to use it.

Last updated: 2026-04-19
