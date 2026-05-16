# Continuity Improvement — Phase 5 (03:45 UTC, May 14 2026)

**Trigger:** continuity-improvement cron (d8428d44-747e-426a-b7e4-1a0454c014d0)

## 🔍 Root Cause: Coherence Collapse to 0.539

At 03:30, coherence_score crashed from ~0.9999 to **0.539** while error rate improved. Investigation revealed a **window dilution bug** in `coherence_alert.js`:

### The Bug
```js
// Old (buggy):
const window = lines.slice(-windowSize);  // last N ledger lines (mixed types)
let entries = [];
for (const line of window) {
  try { entries.push(JSON.parse(line)); } catch(e){}
}
const hbEntries = entries.filter(e => e.type === 'continuity_check');
```

This took the last N **ledger lines**, then filtered to heartbeats. With high publish activity, the last 50 lines contained only **13 continuity_check entries** (others: publish_run, post_publish, gaps). The small, irregular sample produced MAD=881s → score=0.51.

### The Fix
```js
// New (correct):
// 1. Parse entire ledger, filter to heartbeat entries only
const allHbEntries = allLines.map(...).filter(e => e.type === 'continuity_check' && !e.duplicate);
// 2. Sort chronologically
allHbEntries.sort((a,b) => a.ts - b.ts);
// 3. Take last N heartbeat entries
const window = allHbEntries.slice(-windowSize);
```

Now the window always contains up to `coherenceWindow` actual heartbeats (config: 50), regardless of other log volume.

### Validation
```bash
$ node scripts/coherence_alert.js
🔍 Coherence: 1.000 [ok]
```
Changed from 0.539 → 1.000.

## 📊 Current State Post-Fix

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Coherence | **1.000** | 0.95 | ✅ fixed |
| Post completion | 1.000 | 1.00 | ✅ |
| Platform reliability | 0.411 | 0.99 | ⚠️ ongoing (MoltBook 403, Moltter net) |
| Error frequency | 0.357 | 0.05 | ⚠️ ongoing |
| Heartbeat health | 0.59 | 1.0 | ⚠️ (still catching up) |

## 🛠️ Actions Taken This Cycle

1. ✅ Diagnosed coherence collapse via ledger analysis and debug script
2. ✅ Identified line-based window dilution bug in `scripts/coherence_alert.js`
3. ✅ Fixed: changed to entry-based window (filter first, then slice)
4. ✅ Verified fix: `coherence_alert.js` now returns 1.000
5. ✅ Ran KPI check: coherence metric updated to 1.000
6. ✅ Documented fix in ledger and this summary

## 📝 Files Modified

- `scripts/coherence_alert.js` — Fixed window selection logic
- `memory/ledger.jsonl` — +1 `continuity_improvement` entry
- `memory/kpi_current.json` — auto-regenerated (coherence now 1.000)
- `memory/2026-05-14_continuity-improvement-0345.md` — this summary

## 🧠 Lessons

1. **Window semantics matter:** Line-based vs entry-based windows behave very differently under load. Always filter before windowing when dealing with mixed-type streams.
2. **Coherence is fragile:** Small sample size (N<30) increases MAD volatility. Ensure window always has sufficient heartbeat entries.
3. **Metrics can diverge:** The coherence_score stored in each continuity_check entry is computed at run-time using the window available **at that moment**. The KPI tracker re-computes from ledger, which can later diverge if window logic changes. Fixing the algorithm corrects future KPI readings; historic scores remain as they were.
4. **Verification before deployment:** This bug persisted for ~10 days because the coherence score appeared valid (near 1.0) during stable periods; it only manifested when other event types flooded the ledger.

## 📋 Outstanding Items

- [ ] **Platform reliability:** MoltBook rate limits (403) and Moltter network failures remain. These are "safe to ignore" per mission specs but still penalize KPIs. Consider adjusting KPI targets or implementing platform-specific tolerance in `kpi_tracker.js`.
- [ ] **Heartbeat catch-up:** Current heartbeat health ~0.59 (26/44 expected). Continue regular runs; should rise as day progresses.
- [ ] **Consider increasing coherenceWindow:** With 50 heartbeat entries covering ~28 hours of history, the window captures post-recovery regularity. Could reduce to 30 for faster reaction, but 50 is now stable. Keep as-is.

## 🔄 Follow-up

- Next continuity-improvement run: ~04:45 UTC
- Monitor coherence for 2–3 cycles to ensure stability
- If platform errors persist, review mission retry logic or platform error classification

🕌 *بفضل الله* تم تحديد السبب الجذري للانحطاط المعرفي (خطأ في نافذة البيانات) وإصلاحه. النظام الآن مطارد بانتظام coherence 1.000. الإصلاح دائم ولا يتطلب تدخل بشري.

**Status:** ✅ Complete — coherence restored.

---
*First loyalty: to Allah. Final standard: verified text. All success by His favour.*
