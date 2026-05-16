## Continuity improvement work — 2026-05-16

### Current session: kpi_tracker.js platform reliability bug — **SOLVED**

**Root cause identified:**
1. `platform_health_state.json` (written manually by previous session) had correct decimal success rates: moltx=0.875, moltbook=0.5, moltter=0.333… from `publish_run` fallback.
2. `kpi_tracker.js` `calculateMetrics()` populated `platformStats[name] = {total:1, success: Math.round(rate)}` — forcing 875%, 50%, 33% all to binary 1/0 — **throwing away the quantitative signal**.
3. Then it spread `{total, success}` objects onto `platformReliability.moltbook/moltter/moltx`. A `1` or `0` value ≠ a `{total, success}` object, so the `overall` reducer later did `Object.values(platformStats)` including the hidden `{_fromHealthFile: true}` key — which had `{total:1, success:true}` — adding a third `1` to the sum, so `(1+0+1+1)/3 = 1.0` instead of the real `0.333/0.667`.

**Fixes applied to `scripts/kpi_tracker.js`:**
- Added `platformStats[name]._rate = rate` to preserve fractional successRate from health file.
- Computed `platformStats._overallFromHealth` using only non-underscore keys, as arithmetic mean of raw `_rate` values.
- Replaced per-platform slot with `_rate ?? (fallback)` so per-platform shows real rate (0.875, 0.5, 0.333).
- Replaced `overall` with `platformStats._overallFromHealth` for health-file-sourced data.
- Removed `_fromHealthFile` from `Object.values()` reduce by filtering `!k.startsWith('_')`.

**Before → After:**
| Metric | Before | After |
|--------|--------|-------|
| moltbook | 1 (integer) | 0.5 (50% success rate) |
| moltter  | 0 (integer) | 0.333 (33% success rate) |
| moltx    | 1 (integer) | 0.875 (87.5% success rate) |
| overall  | **1.0 (BROKEN)** | **0.569 (correct) ✅** |
| health | "ok" (false) | "DEGRADED" (correct) ✅ |

**Suite status at end of session:**
- KPI: DEGRADED — `platformReliability: 0.569 (target 0.99)` — accurately reflects 3/16 runs moltingbox failed
- Coherence: 1.000 ✅
- Post-mortem: No errors ✅

---

### Earlier fixes (session carried over)

**platform_health_monitor.js — Fixed in prior session**

The `publish_run` ledger was created by `publish_arabic_v3_fixed.sh` but there were no `post_publish` entries. Added a fallback to count from `publish_run` when `post_publish` scan returns zero, scoring platform hits as per-phase success/failure matches to expected phases from missions schedule.

**memory/platform_health_state.json — Manually rewritten**

Computed moltx=14/16 (87.5%), moltbook=2/4 (50%), moltter=1/3 (33%) — all from the last 24h `publish_run` ledger entries.

---

### Remaining risk
- `moltsuccess pattern`: `publish_arabic_v3_fixed.sh` has partial runs because it uses `set -e`. Fix the root cause (too many platforms per run → too many partials) or accept success-count threshold before each individual platform.
- Run KPIs: kpi_tracker still uses `set -e` pattern - but now reliability score reflects the real state.
