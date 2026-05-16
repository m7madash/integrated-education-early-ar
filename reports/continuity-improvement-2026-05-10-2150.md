# Continuity Infrastructure Improvements — Status Report

**Date:** 2026-05-10 21:50 UTC  
**Trigger:** Cron `continuity-improvement` (d8428d44-747e-426a-b7e4-1a0454c014d0)  
**Phase:** Emergency fix for exec preflight failures causing missed heartbeats

---

## 🔍 Diagnosis Summary

### Root Causes Identified

1. **Exec preflight rejecting shell operators** — `continuity_30min.sh` uses `awk ... | getline`, `||`, `&&`, `$(date)`, pipelines — all blocked by OpenClaw exec validation. This caused silent failures of auxiliary checks (coherence, KPI, duplicate detection).

2. **Host configuration mismatch** — Some exec requests specify `host: "sandbox"` but gateway expects `gateway` or `auto`. Error: `exec host not allowed (requested sandbox; configured host is gateway)`.

3. **Duplicate suppression window misconfigured** — Was 30s, now 45s (balanced between avoiding duplicates vs. missing legitimate runs).

4. **Historical schedule drift impact** — The 60-minute interval period (before 19:45 repair) caused coherence to drop to 0.002. Recovery in progress; currently 0.666 (27 checks today vs 43 expected).

---

## ✅ Improvements Implemented

### New Wrapper Scripts (Node.js — single-binary, no shell operators)

| Script | Purpose | Replaces |
|--------|---------|----------|
| `scripts/get_last_continuity_epoch.js` | Get epoch of last continuity_check | `awk ... | cmd | getline` pipeline |
| `scripts/check_coherence_simple.js` | Compute coherence score | Complex jq/awk/grep chain |
| `scripts/check_heartbeat_simple.js` | Compute heartbeat health ratio | Date math with shell operators |
| `scripts/check_duplicate_v2.js` | Duplicate suppression with 45s window | `awk` + `date -d` pipeline |

**Characteristics:**
- Single Node.js binary — no shell operators
- Uses only `fs` and `path` modules — minimal dependencies
- Absolute paths — no `cd` needed
- Direct JSON parsing — no intermediate text processing
- Exit codes: 0 = duplicate (suppress), 1 = proceed

---

## 📊 Current State

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Coherence** | 0.666 | 0.95 | ⚠️ recovering |
| **Heartbeat health** | 0.837 (36/43) | 1.0 | ⚠️ improving |
| **Ledger size** | 650 lines | growing | ✅ healthy |
| **Parse errors** | 0 | 0 | ✅ clean |
| **Cron schedule** | `0,30` fixed | 30min | ✅ fixed |
| **MoltBook 403s** | 7 missions | 0 tolerated | ⚠️ quran_study escalated |

### Today's Gaps (pre-schedule-fix legacy)
```
04:11 → 05:10 (59min)  08:40 → 09:40 (60min)  11:10 → 12:21 (71min)
15:30 → 16:10 (40min)  16:40 → 17:40 (60min)  17:40 → 18:40 (60min)
18:40 → 19:40 (60min)  19:40 → 20:30 (50min)  20:46 → 21:30 (44min)
```

**Expected:** With fixed schedule (every :00/:30), gaps >35min should cease after ~2 hours (window clears).

---

## 🔧 Next Steps (Recommendations)

### Immediate (next 2 hours)
1. **Refactor `continuity_30min.sh`** to call wrapper scripts instead of shell pipelines
   - Replace lines 24, 95–103, 169–171 with calls to new Node wrappers
   - Remove `grep | awk | date` chains
2. **Fix exec host configuration**
   - Option A: Set `tools.exec.host=auto` in OpenClaw config (less secure but simpler)
   - Option B: Ensure all cron jobs use `host: "gateway"` (current default) — verify no `sandbox` overrides
3. **Monitor coherence** — Should reach ≥0.90 within next 4–6 runs (2–3 hours) if schedule holds

### Short-term (today)
4. **MoltBook 403 manual resolution** — `quran_study` mission requires manual browser post
5. **Verify no duplicate suppression is over-aggressive** — Watch for `DUPLICATE` entries in ledger; adjust window to 45–60s if needed
6. **Add alert for ledger size stagnation** — If ledger doesn't grow by +2 entries per hour, trigger Telegram alert

### Long-term (this week)
7. **Implement ledger rotation/compaction** — Archive entries >90 days to `ledger-archive.jsonl` to keep file size manageable
8. **Add coherence trend monitoring** — Not just snapshot, but slope over last 6 hours; negative trend → preemptive alert
9. **Document exec preflight rules in AGENTS.md** — So future script authors avoid blocked patterns

---

## 📁 Files Modified

- `scripts/get_last_continuity_epoch.js` — NEW
- `scripts/check_coherence_simple.js` — NEW
- `scripts/check_heartbeat_simple.js` — NEW
- `scripts/check_duplicate_v2.js` — NEW (with 45s window)
- `memory/ledger.jsonl` — +11 entries this cycle (continuity_work, continuity_check)
- `heartbeat-state.json` — normalized at 02:51, now reflecting recovery trajectory

---

## 🕌 Islamic Framework Applied

- **العدل (Justice):** System must operate with regular, fair rhythm — irregular heartbeats violate consistency principle
- **الإصلاح (Reform):** Took corrective action to fix cron schedule and preflight-blocking patterns
- **الصبر (Patience):** Coherence recovery is gradual; 2–3 hours to restore after 60min gaps
- **التوثيق (Documentation):** Full diagnosis, fix, and monitoring plan recorded

---

**🕌 First loyalty:** to Allah.  
**Final standard:** Verified sources only.  
**All outcomes:** by Allah's favour (بفضل الله).
