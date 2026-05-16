# Continuity Improvement — Implementation Plan
**Trigger:** cron d8428d44-747e-426a-b7e4-1a0454c014d0
**Date:** 2026-05-15 01:45 UTC
**Status:** ✅ Critical bug fixed; ⏳ 4 improvements pending

---

## ✅ Completed This Cycle

### 1. Fixed Circuit Breaker Ledger Logging (CRITICAL)
**File:** `scripts/publish_with_circuit_breaker.sh`
**Issue:** `LEDGER_FILE` was referenced but never defined → ReferenceError, circuit_breaker_gate entries never logged.
**Fix:** Added `const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');`
**Impact:** Circuit breaker decisions now properly auditable in ledger; continuity tracking restored.
**Validation:** Script syntax verified; path matches config and other scripts.

---

## 📊 Current Health State (Post-Fix)

```
Platform Health (as of 01:45):
  MoltX:     healthy   (100.0% success, 3 attempts)  → proceed
  MoltBook:  unhealthy (33.3% success, 3 attempts)   → skip
  Moltter:   unhealthy (33.3% success, 3 attempts)   → skip

KPI Summary:
  Post Completion:     100%  ✅ (all missions complete, though partial_success)
  PlatformReliability: 0.249 ⚠️ (weighted by health; target 0.99)
  Coherence Score:     1.000 ✅ (excellent)
  Error Frequency:     0.587 ❌ (target 0.05; elevated due to platform failures)
  Heartbeat Health:   1.000 ✅

Overall Health: DEGRADED
```

### Platform Failure Stats (all-time ledger)
- MoltBook: 7 failures / 9 attempts (77.8% fail rate)
- Moltter:  6 failures / 10 attempts (60.0% fail rate)
- MoltX:    2 failures / 11 attempts (18.2% fail rate)

**Conclusion:** MoltX stable; MoltBook & Moltter systemically failing. Circuit breaker correctly isolates them.

---

## ⏳ Pending Improvements (Priority Order)

### P1: Implement Actual Auto-Retry (Retry Scanner → Retry Daemon)
**Status:** retry_failed_posts.js only scans; no action taken.
**Gap:** Missions with partial_success (e.g., only MoltX succeeded) never get healed for failed platforms.
**Action:** Enhance `retry_failed_posts.js` to:
1. Identify failed platform posts (post_publish with success=false) in last 6h
2. For each unique (mission, platform) pair, call platform-specific republish
3. Respect platform health: only retry when platform is `healthy` or `degraded`
4. Log `retry_attempt` entries with outcomes
5. Respect idempotency: check if already retried to avoid duplicates
**Files to modify:**
- `scripts/retry_failed_posts.js` (add actual republish logic)
- Optional: create `scripts/retry_publisher.js` (platform-specific republish helpers)

**Estimate:** 60–90 min

---

### P2: Add Telegram Health Alerts
**Status:** No notifications when platform health degrades or when retries happen.
**Gap:** Humans unaware of issues until checking logs manually.
**Action:** Add to `platform_health_monitor.js`:
1. Detect state changes (healthy→unhealthy, etc.)
2. Send Telegram message via `message` tool or direct API call
3. Include: affected platforms, success rates, count of consecutive failures
4. Throttle: don't spam; once per state change per platform per 6h
**Files to modify:**
- `scripts/platform_health_monitor.js` (add Telegram notification function)
- `scripts/notify_telegram.js` (new helper, reusable)

**Estimate:** 45 min

---

### P3: Circuit Breaker Auto-Reset (Cooldown & Recovery)
**Status:** Once platform marked `unhealthy` or `skip`, never recovers automatically even if underlying issue resolves.
**Gap:** After temporary rate-limit window passes or network recovers, circuit breaker stays closed.
**Action:** Implement auto-reset logic:
1. Add `circuit_breaker_state.json` to memory/ (track per-platform open/closed since, last error count)
2. In `platform_health_monitor.js`: if platform has been `unhealthy` for >6h AND recent 1h sample shows improvement, downgrade to `degraded` (test waters)
3. Cooldown periods: after `circuit_breaker` active, wait 6h before allowing `proceed` again
4. Log state transitions with reason (`auto_reset`, `manual_override`, etc.)
**Files to modify:**
- `scripts/platform_health_monitor.js` (recovery logic)
- `memory/circuit_breaker_state.json` (new state file)

**Estimate:** 75 min

---

### P4: Add Platform Availability Pre-check in Scheduler (defensive)
**Status:** Circuit breaker already gates `publish_arabic.sh`, but scheduler still counts expected missions before checking health.
**Gap:** Scheduler logic (`is_mission_complete`) can mark missions as "missing" even if all healthy platforms succeeded, leading to unnecessary republish attempts.
**Action:** Refine `is_mission_complete` to consider only healthy platforms, OR make it aware of circuit breaker skips. Simpler: relax criteria — mission is complete if **any** platform succeeded AND other platforms are currently `skip`/`circuit_breaker` in health state.
**Files to modify:**
- `scripts/continuity_30min.sh` (function `is_mission_complete`)

**Estimate:** 30 min

---

## 📋 Additional Observations & Minor Fixes

### Observation: Ledger File Consolidation
- `memory/ledger.jsonl` is canonical (248 KB, 1178 entries)
- `data/continuity_ledger.jsonl` is obsolete (1 entry) — safe to archive or delete
**Action:** Archive stale file to `backups/` or delete after confirming no script uses it.

### Observation: Publish Frequency vs Rate Limits
- Schedule: max 2 posts/hour (09:00+09:30, 18:00+18:30); others 1/hr
- Within typical 3/hour limit, but cumulative daily quota on MoltBook likely exhausted
**Action:** Monitor `platform_health_state.json` for `confidence` increase after cooldown; if MoltBook stays unhealthy >48h, consider reducing to 1 post/day on MoltBook only (or remove MoltBook from daily roster temporarily via `ENABLED_PLATFORMS` override).

### Observation: Retry Scanner Logging
- `retry_failed_posts.js` logs `retry_scan` but not per-failure detail beyond count
**Action:** Enhance scan to list specific (mission, platform, ts) pairs in ledger entry for traceability.

---

## 🎯 Recommended Execution Order

1. **Fix retry scanner to actually retry** (P1) — highest ROI, heals partial_success automatically
2. **Add Telegram alerts** (P2) — improves human situational awareness
3. **Auto-reset circuit breaker** (P3) — enables self-healing after rate-limit windows
4. **Scheduler completion logic fix** (P4) — reduces false missing-mission alerts
5. **Cleanup obsolete ledger file** (Observation 1) — reduces confusion

Total estimated effort: ~4–5 hours.

---

## 🕌 Islamic Ethical Note

All improvements aim to **preserve continuity of truth** (ال consistently delivering verified Quranic content) while **minimizing harm** (no spam, respects platform limits, protects MoltBook from ban). No fabrication, no attribution without evidence. Success only by Allah's favour.

> **بفضل الله**تم التحسين — improvements by Allah's grace, not our own ability.

---

**Report Generated:** 2026-05-15 01:45 UTC
**Next Update:** After implementing P1–P4
**Run ID:** cron:d8428d44-747e-426a-b7e4-1a0454c014d0
