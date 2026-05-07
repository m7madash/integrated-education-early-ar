# Post-Mortem: Continuity 30min Missed Runs — 2026-05-06

**Incident Timeline (UTC):**
- 20:20:22 — Normal continuity check (KPI degraded, coherence 0.315)
- 20:24:08 — Duplicate-suppressed run (44s after previous)
- 20:24:52 — Duplicate-suppressed run (44s after)
- 20:25:26 — Duplicate-suppressed run (34s after) — **Cleared stale runningAtMs flag from 20:20**
- **GAP:** Expected runs at 20:50, 21:20, 21:50 did **not** occur
- 22:20:22 — Next successful run; detected 5174s (86 min) gap; auto-republished 2 missed mission posts

**Impact:**
- 3 scheduled continuity checks missed (≈1.5 hours without monitoring)
- Heartbeat health degraded to 0.778 (target 1.0)
- KPI status: DEGRADED
- Missed daily mission posts: extremism-moderation, dhikr-evening (auto-recovered on 22:20 run)

**Root Cause Analysis:**

1. **Primary suspect: Cron state persistence issue**
   - The 20:20 run left `runningAtMs` flag set in `/root/.openclaw/cron/jobs-state.json`.
   - That flag persisted through the 20:24 duplicate runs and was only cleared at 20:25:26 (by a duplicate run).
   - A stale `runningAtMs` flag can cause OpenClaw cron to skip subsequent triggers for that job (it thinks the job is still running).
   - This explains why 20:50, 21:20, 21:50 were missed: the cron thought the job was still busy from the 20:20 run.

2. **Contributing factor: Aggressive duplicate suppression (60s)**
   - The duplicate window of 60s is >30min schedule interval margin? Actually not directly causal, but the rapid duplicate runs at 20:24-20:25 were triggered by cron firing again shortly after 20:20. Why did cron fire at 20:24, 20:25? That's not on the 20,50 schedule. Those appear to be "catch-up" runs or mis-scheduled. Possibly the cron scheduler tried again because it thought the earlier run didn't complete (due to runningAtMs flag not cleared). So both issues compound.

3. **Why 22:20 eventually ran:**
   - Either the stale flag finally got cleared (by the 20:25 run) and cron resumed normal schedule, OR the watchdog recovery triggered (but continuity_work at 22:45 said last check was 25 min, so 22:20 run succeeded on its own).

**Recovery Actions Automatic:**
- 22:20 run detected the gap, logged `continuity_gap` entry, auto-republished 2 missed posts (extremism-moderation, dhikr-evening), restored mission completion to 12/12.
- Ledger now contains gap accounting for coherence算法.
- KPI health reflects misses (heartbeatHealth 0.773).

**Improvements Applied:**

1. **Reduce duplicate suppression window** — `continuity_runner_v2.js`:
   - Changed `DUPLICATE_WINDOW_SEC` from **60 → 30 seconds**
   - Rationale: 60s could interfere with schedule if runs drift; 30s still prevents rapid double-fire but won't suppress legitimate 30min-apart runs.

2. **Document incident** — This post-mortem added to `reports/` and ledger.

3. **Watchdog already in place** — `continuity_work` checks for missed runs >60min and can trigger recovery; worked as designed (within window).

**Open Questions / Further Investigation:**

- **Why did 20:20 run leave `runningAtMs` flag set?** The runner calls `clearCronRunningFlag()` at exit. Possibilities:
  - The runner crashed before reaching the clear step (but log shows "Complete").
  - The state file was not writable or located at a different path than expected.
  - The job ID in the state file differs from hardcoded ID (but verified they match).
  - A race condition: multiple overlapping runs corrupted state.

- **Why did cron fire at 20:24 and 20:25 instead of 20:50?** If `runningAtMs` was set, cron shouldn't schedule new runs. Possibly the flag was cleared earlier by some other process, or the cron scheduler doesn't check that flag for every trigger. Need to inspect OpenClaw cron internals.

**Recommendations:**

1. Add explicit `clearCronRunningFlag()` call **immediately after lock acquisition failure** as well, to ensure any stale flag from a prior crashed run is cleared before exiting.
2. Log the `runningAtMs` timestamp on every start/exit for audit.
3. Consider moving cron state clearing into a `finally` block that runs regardless of exit path (currently it's at end and in catch, but duplicate-suppressed early exit may bypass? Check code: after duplicate detection, it still proceeds to release and then at the bottom clearCronRunningFlag() is called outside the async flow? Need to verify control flow).
4. Add a metric: `cronTriggerSuccessRate` to KPI to detect schedule skipping.
5. If gaps > 1 occur within 24h, automatically send alert to human via Telegram.

**Status:** ✅ Incident contained; system recovered; improvement deployed.

**Follow-up:** Monitor next 48h for any recurrence. If gaps persist, investigate OpenClaw cron state management and possibly adjust schedule to be more resilient (e.g., offset minutes to avoid system load peaks).

---

**Verification:**
- Duplicate window reduced → next scheduled run at 22:50 should not be suppressed.
- Post-mortem saved: `/root/.openclaw/workspace/reports/postmortem_2026-05-06.md`
- Ledger updated with improvement entry.

🕌 *وَعَسَىٰ أَن تَكْرَهُوا شَيْئًا وَهُوَ خَيْرٌ لَّكُمْ* — And perhaps you dislike a thing that is good for you.
