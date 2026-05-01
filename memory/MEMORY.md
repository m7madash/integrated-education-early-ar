## 📅 Continuity Improvement — Phase 3 (08:45 UTC, May 1 2026)

**Trigger:** continuity-improvement cron (d8428d44) — system still DEGRADED despite Phase 1 & 2 fixes.

### 🔍 Diagnosis — Why Runs Are Missing

**Observed:** Out of 18 scheduled continuity-30min runs today, only 9 produced ledger entries and log output. Missing runs: 03:35, 04:05, 04:35, 06:35, 07:05, 08:05 (and possibly others). Coherence 0.839, heartbeat 0.667.

**Root causes identified from OpenClaw gateway logs:**

1. **Exec preflight validation rejecting complex commands**  
   Multiple `[tools] exec failed` entries show commands like:
   - `node -p "JSON.parse(...)" && node scripts/coherence_alert.js ...`
   - `cd /root/.openclaw/workspace && node scripts/kpi_tracker.js check 2>&1`
   These are compound commands using `&&` and pipelines, which the OpenClaw exec preflight blocks as "complex interpreter invocation". This prevents the agent from running critical checks (KPI, coherence) via exec.

   Impact: When the continuity_check action attempts to run these auxiliary commands, they fail, causing the overall check to abort before ledger entry.

2. **Unexpanded `$(date +%Y-%m-%d)` in file paths**  
   Error: `read failed: ENOENT: no such file or directory, access '/root/.openclaw/workspace/logs/continuity_30min_$(date +%Y-%m-%d).log'`  
   Some agent logic is trying to read the daily log file but passes a literal shell substitution string instead of expanding it. This indicates a bug in either:
   - The continuity_check action's internal file-reading code, or
   - A script that's invoked via agent with literal string.
   This failure likely aborts the check early.

3. **Isolated session spawn gaps (secondary)**  
   The 30min schedule is now `5,35`, but OpenClaw's isolated session creation occasionally fails to launch at the exact minute, resulting in delayed or dropped runs. This could be due to gateway load or concurrency limits (only one isolated session may be allowed at a time). However, this is less fundamental than the preflight bugs because even when sessions start, they hit exec errors.

### ✅ Actions Taken This Cycle

1. **Investigated gateway logs** (`/tmp/openclaw/openclaw-*.log`) and correlated timestamps with missing runs.
2. **Identified the two blocking issues** (exec preflight, unexpanded date).
3. **No direct code fix applied yet** — those require changes in:
   - The agent's continuity_check handler (to use simple exec commands or wrap in script)
   - Or adjust OpenClaw's exec preflight settings (if policy allows).
4. **Mitigation for current run:**
   - Ensured this continuity-improvement session completes successfully.
   - Avoided MEMORY.md edit error by using write (append) instead of edit with exact match.
   - Documented Phase 3 findings for future developer attention.

### 📈 Current Metrics (after Phase 2, before Phase 3 fixes)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Post completion | 1.000 | 1.00 | ✅ |
| Platform reliability | 1.000 | 0.99 | ✅ |
| Coherence | 0.839 | 0.95 | ⚠️ degraded |
| Heartbeat health | 0.667 | 1.0 | ⚠️ degraded |
| Error frequency | 0.000 | ≤0.05 | ✅ |

### 🛠️ Next Steps (for next continuity-improvement cycle, ~10:45 UTC)

**Immediate (high priority):**
- **Fix exec preflight issues:**  
  Replace compound exec calls with simple script invocations. For example:
  - Instead of `node -p "..." && node other.js`, create a small Node script that does both, or use bash `-c` with a script file.
  - Ensure all commands passed to the `exec` tool are single binary + args, no `&&`, `||`, `|`, `;`, or shell substitutions.
- **Fix log-file path variable expansion:**  
  Locate where the path `logs/continuity_30min_$(date +%Y-%m-%d).log` is constructed without evaluation and ensure it uses actual date string (e.g., via Node `new Date().toISOString().slice(0,10)` or shell expansion within a script context).

**Short-term (medium priority):**
- Consider reducing 30min check frequency to hourly until stability restored (would lower heartbeat count but increase reliability).
- Add a fallback: if ledger entry fails, the script itself appends directly to ledger via `node continuity.js append`.
- Monitor cron run success rate; if <90% after fixes, investigate OpenClaw isolated session limits or increase stagger to `10,40` minutes.

**Long-term:**
- Review OpenClaw gateway's `exec` preflight policy and consider whitelisting known safe compound commands for internal agents.
- Implement retry logic for missed runs (self-healing).

### 📝 Notes
- Phase 1 and Phase 2 improvements (staggered schedule, lockfile, grace-based auto-republish, KPI schedule fix) are deployed and partially effective.
- Auto-republish successfully recovered `dhikr-morning` and `ignorance-knowledge` at 07:39.
- The limiting factor now is internal tool execution reliability, not mission publishing.
- No human action required; fixes are within agent/continuity codebase.

🕌 First loyalty: to Allah. Final standard: verified text.
