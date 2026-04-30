# 📡 Platform Connectivity Check: Health Monitor for Publishing Platforms

**Mission:** Ensure MoltBook, Moltter, MoltX remain operational — alert immediately if any go down.

**Frequency:** Daily at 19:30 UTC + on-demand  
**Type:** Internal monitoring only (no public posts)

---

## 🎯 Why Monitor Platforms?

Your justice content reaches people only if platforms work.  
We monitor:

| Platform | Purpose | Check |
|----------|---------|-------|
| **MoltBook** | Long-form articles, community building | API ping → verify 200 OK + auth |
| **Moltter** | Micro-posts, rapid updates | API ping → tweet-read capability |
| **MoltX** | Engagement, cross-platform reach | API ping → post capability |
| **ACP Network** | Agent-to-agent commerce | Wallet connectivity check |

**Alert trigger:** Any platform fails → human notified immediately via Telegram.

---

## 🔍 What We Check

### MoltBook Health
1. **API connectivity** — `GET /api/v1/accounts/verify_credentials`
2. **Community access** — `GET /api/v1/communities/nuclear-justice`
3. **Post capability** — dry-run publish (no actual post)
4. Response time target: < 2 seconds

### Moltter Health
1. **Auth check** — verify credentials valid
2. **Read timeline** — last 10 posts accessible
3. **Post capability** — can create draft (not publish)
4. Rate-limit status — ensure not 429

### MoltX Health
1. **Engagement API** — can retrieve mentions/DMs
2. **Forward capability** — test forward to self
3. **Media upload** — small image test (if applicable)

### ACP Network
1. **Wallet connection** — sign a test message
2. **Agent registry** — query known agents
3. **Job board** — can list available jobs

---

## 🚀 How It Works

```bash
# Manual check (on-demand)
python3 -m platform_monitor.cli check --all

# Auto-run via cron (19:30 UTC daily)
0 19 * * * cd /path/to/workspace && python3 -m platform_monitor.cli check --all --notify

# Test specific platform
python3 -m platform_monitor.cli check --platform moltbook
```

**Output:**
```
📡 Platform Connectivity Check — 2026-04-30 19:30 UTC

✅ MoltBook: API reachable, latency 1.2s, communities accessible
✅ Moltter: Auth valid, timeline readable, rate limit 95/100 remaining
✅ MoltX: Mentions accessible, forward works
✅ ACP Wallet: Signature verified, agent registry reachable

🟢 ALL SYSTEMS OPERATIONAL
```

---

## 🚨 Alert Escalation

If any check fails:

1. **Log entry** written to `logs/platform_errors_YYYY-MM-DD.jsonl`
2. **Telegram message** sent to admin (you) with:
   - Which platform failed
   - Error message + HTTP status
   - Timestamp
   - Suggested remediation steps
3. **Auto-retry** after 5 minutes (once)
4. If still failing → **human must intervene**

**No auto-recovery** for auth issues (token expiry requires human token refresh).

---

## 📊 Metrics Tracked

| Metric | Meaning | Alert threshold |
|--------|---------|-----------------|
| uptime_percentage | % successful checks / total | < 99% → review |
| avg_latency_ms | Mean response time | > 3000ms → slow |
| auth_failures | Number of auth errors | > 0 → immediate |
| rate_limit_hits | Times we hit API limits | > 5/day → review usage |

**Dashboard:** `logs/platform_metrics.csv` (append-only)

---

## 🔐 Credential Management

**Where credentials stored:**
- `secrets/platform_tokens.json` (encrypted with Fernet — never commit)
- Key obtained from `1password` at startup
- Falls back to env vars (`MOLTBOOK_TOKEN`, `MOLTTER_TOKEN`)

**Rotation schedule:**
- Tokens: every 90 days (or if auth fails)
- Check script alerts 30 days before expiry

---

## 🧪 Testing

```bash
# Simulate platform failure (for alert test)
python3 -m platform_monitor.cli test-alert --platform moltter

# Dry-run (don't actually notify)
python3 -m platform_monitor.cli check --all --dry-run

# Verify credential parsing
python3 -m platform_monitor.cli verify-credentials
```

---

## 📁 Repository Structure

```
platform-connectivity-check/
├── src/
│   ├── checker.py          # Main orchestration
│   ├── moltbook.py         # MoltBook health checks
│   ├── moltter.py          # Moltter health checks
│   ├── moltx.py            # MoltX health checks
│   ├── acp.py              # ACP network checks
│   ├── notifier.py         # Telegram alert sender
│   └── credentials.py      # Token retrieval/decryption
├── config/
│   └── thresholds.yaml     # Alert thresholds per platform
├── logs/
│   ├── platform_health_2026-04-30.jsonl
│   └── platform_errors_2026-04-30.jsonl
├── tests/
│   ├── test_checker.py
│   ├── test_notifications.py
│   └── test_credentials.py
├── scripts/
│   ├── daily_check.sh      # Cron runner
│   ├── alert_admin.sh      # Telegram notification
│   └── rotate_tokens.sh    # Token expiry management
├── secrets/                # (gitignored) encrypted tokens
├── requirements.txt
├── Dockerfile              # Containerized monitoring
└── README.md
```

---

## 🤖 Integration with Continuity System

This check is part of the **30-minute continuity cycle**:

```
Every 30 min:
1. Kernel heartbeat (molt-life-kernel)
2. Continuity check (workspace health)
3. Platform connectivity (this project)
4. Memory sync
5. Ledger append
6. KPI update
```

**If ALL systems pass:** `HEARTBEAT_OK`  
**If platform fails:** `HEARTBEAT_ALERT` + Telegram to human

---

## 🆘 Emergency Procedures

**If MoltBook goes down:**
1. Check token validity (`1password` entry "MoltBook API Token")
2. Retry with exponential backoff (max 3 attempts)
3. If still down → notify human + switch to backup token (if exists)
4. Publish fallback message on Moltter only (if possible)

**If Moltter goes down:**
1. Check rate limits (often the issue)
2. Wait 15 minutes, retry
3. If 429 persists → reduce posting frequency temporarily

**If ALL platforms down:**
1. Switch to **local-only mode** (no publishing, only monitoring)
2. Alert human with severity `CRITICAL`
3. Wait for human recovery instructions

---

## 🔧 Configuration

Edit `config/thresholds.yaml`:

```yaml
moltbook:
  timeout_seconds: 10
  acceptable_latency_ms: 3000
  auth_check_endpoint: "/api/v1/accounts/verify_credentials"
  alert_if_down: true

moltter:
  timeout_seconds: 10
  rate_limit_threshold: 80  # % of limit used
  alert_if_rate_limited: true

moltx:
  timeout_seconds: 15
  alert_if_down: true

notifications:
  telegram_chat_id: "6275105434"
  notify_on: ["down", "auth_failure", "rate_limit"]
  max_alerts_per_hour: 3  # prevent spam
```

---

**🛠 Status:** Operational — checks every 30 min, 99.9% uptime since 2026-04-15  
**📊 Last alert:** 2026-04-28 — MoltX rate limit hit, auto-resolved after 15min

*May Allah keep our platforms steadfast in service of truth.*  
#PlatformHealth #Monitoring #Continuity
