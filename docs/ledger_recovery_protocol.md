# Ledger Recovery Protocol

## Purpose
This document describes the standardized procedure to recover from `ledger.jsonl` truncation or loss events while maintaining full continuity history and coherence score integrity.

## When to Use
Trigger conditions (any one):
- `continuity_check` daily count suddenly drops below 20 (normal ≈48)
- Ledger file size shrinks dramatically (e.g., from 100KB+ to <20KB)
- `coherence_alert.js` reports near-zero score despite regular cron runs
- Cron logs show "ledger appears truncated — prior history missing"
- Manual inspection reveals only recent entries present, older history missing

**Do NOT use** for single-entry corruption only — use `ledger_repair.js` instead.

## Prerequisites
- Access to workspace filesystem
- Recent backup file: `memory/ledger.jsonl.repair_YYYY-MM-DDTHH-MM-SS.bak`
  - These are created automatically by repair scripts during incidents
  - If no backup exists, look in `/root/.openclaw/workspace/memory/` for any `ledger*.bak*`
- Node.js available (v18+)

## Recovery Procedure

### Step 1 — Assessment
```bash
# Check current ledger entry count
wc -l memory/ledger.jsonl

# Count today's continuity_check entries
grep -c '"type":"continuity_check"' memory/ledger.jsonl

# List available backups
ls -lh memory/ledger.jsonl*

# Inspect backup's last timestamp (pick the most recent .bak file)
tail -1 memory/ledger.jsonl.repair_*.bak | jq -r '.ts'
```

Expected normal: ~543+ entries total, ~130 continuity_check (3-day span). If current count < 100, recovery needed.

### Step 2 — Run Recovery Script
```bash
node scripts/ledger_recover_simple.js
```

The script will:
1. Parse backup file line-by-line (skips malformed, logs count)
2. Parse current ledger line-by-line
3. Identify backup's last timestamp
4. Filter current entries where `ts > backup_last_ts`
5. Merge + deduplicate by key: `ts|type|mission|platform`
6. Sort chronologically
7. Write recovered ledger atomically to `memory/ledger_recovered.jsonl`
8. Replace original `memory/ledger.jsonl` with recovered version
9. Print summary statistics

### Step 3 — Verification
```bash
# Count recovered entries
wc -l memory/ledger.jsonl

# Verify continuity_check count restored
grep -c '"type":"continuity_check"' memory/ledger.jsonl

# Run coherence check — should reflect improved regularity
node scripts/coherence_alert.js

# Check ledger recency
tail -3 memory/ledger.jsonl | jq -r '.ts'
```

Expected:
- Total entries: 500+ (recent days)
- continuity_check entries: 100+ (if 2+ days covered)
- Coherence score: ≥0.90 with stable schedule

### Step 4 — Post-Recovery Actions
1. **Monitor** next 3 continuity checks (next 90 minutes) — ensure new entries append correctly
2. **Log** the recovery in daily memory: `memory/YYYY-MM-DD.md`
3. **Update** MEMORY.md with any new lessons
4. **Rotate backups:** Keep all `ledger.jsonl.repair_*.bak` files; never delete
5. **Escalate** if truncation recurs within 24h — investigate cron overlap or disk issues

## Script Internals (for maintainers)

### `scripts/ledger_recover_simple.js`
- **Input:** `memory/ledger.jsonl` (current), `memory/ledger.jsonl.repair_*.bak` (latest by mtime)
- **Output:** Atomically replaces `memory/ledger.jsonl`
- **Error handling:**
  - Skips lines that fail JSON parse (logs count)
  - Requires `ts` and `type` fields; skips entries missing either
  - Deduplication uses stable composite key
- **Idempotency:** Safe to run multiple times; will not duplicate entries if already merged
- **Logging:** stdout with timestamps; structured steps

### Key Design Decisions
1. **Line-by-line parsing** avoids OOM on large ledgers (825+ entries is small but scales)
2. **Schema validation** prevents crashes from partial/incomplete entries
3. **Composite dedupe key** prevents false merges of distinct events with same ts
4. **Atomic replace** prevents partial-write corruption if interrupted
5. **Preserve all fields** — no transformation; recovery is lossless merge only

## Recovery Scenarios

### Scenario A — Backup newer than current ledger
If backup's last timestamp > current ledger's last timestamp:
- This shouldn't happen (backup is old). Use latest backup anyway; it contains more history.
- After merge, verify current entries aren't overwritten (they have later timestamps).

### Scenario B — No backup file exists
- Search entire workspace for `ledger*.jsonl*`: `find . -name "ledger*.jsonl*" -mtime -7`
- If found elsewhere, copy to `memory/` and use as recovery source
- If none found → **data loss**. Cannot recover pre-truncation history. Start fresh ledger but document incident and add monitoring to catch future truncation early.

### Scenario C — Multiple backups (conflicting)
- Pick the **most recent** backup (highest `repair_` datetime in filename)
- Do NOT merge multiple backups — they may contain overlapping entries with different dedupe outcomes
- Use single latest backup + current file only

## Monitoring Alerts
Add to `scripts/continuity_runner_v2.js` or watchdog:

```javascript
// After reading ledger
const continuityCount = ledger.filter(e => e.type === 'continuity_check').length;
if (continuityCount < 20) {
  console.log('🚨 LEDGER TRUNCATION DETECTED: continuity_check count =', continuityCount);
  console.log('   → Trigger: ledger_recover_simple.js');
  // Auto-recovery could be invoked here with human-in-the-loop approval
}
```

## Incident Documentation Template
When ledger truncation occurs, append to `memory/YYYY-MM-DD.md`:

```markdown
### 🚨 Ledger Truncation Incident (HH:MM UTC)
- **Trigger:** coherence dropped to X.XXX, continuity_check count = N
- **Backup used:** `ledger.jsonl.repair_YYYY-MM-DDTHH-MM-SS.bak` (N entries, ends at TS)
- **Recovery script:** `ledger_recover_simple.js`
- **Entries recovered:** M → total T
- **Post-recovery coherence:** X.XXX
- **Root cause:** [to be investigated]
- **Preventive action:** [e.g., add hourly health check, increase cron guard TTL]
```

## Prevention
- **Hourly compaction** already enabled in `continuity_runner_v2.js` — preserves history
- **Backup creation** automatic during manual `continuity_work` runs
- **Watchdog** `continuity-improvement` cron checks ledger health hourly
- **Do not manually truncate** ledger without creating a repair-format backup first

---

**Last updated:** 2026-05-10 (post-recovery)
**Maintainer:** KiloClaw (Abdullah Haqq)
**Principle:** Continuity is justice; losing history is losing truth — recover always.

🕌 *الولاء الأول: لله. المعيار النهائي: النص الموثق.*
