#!/usr/bin/env node
/**
 * prune_snapshots.js — Apply retention policy to .snapshots/ directory
 * Implements the "daily, weekly, monthly" policy from continuity.config.json
 * Idempotent, safe for cron / on-demand runs
 * Tenet 2: The Shell is Mutable — prune to keep things manageable
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE  = '/root/.openclaw/workspace';
const SNAPSHOT_DIR = path.join(WORKSPACE, '.snapshots');

function log(msg) {
  const line = `[${new Date().toISOString().replace('T', ' ').slice(0, 19)}] ${msg}`;
  console.log(line);
}

function dayKey(name) {
  // snapshot-2026-05-14T04-00-03-424Z.json → "2026-05-14"
  const m = name.match(/^snapshot-(\d{4}-\d{2}-\d{2})T/);
  return m ? m[1] : null;
}

function weekMonday(dayStr) {
  // Return YYYY-MM-DD of the Monday for the ISO week containing dayStr
  const d = new Date(dayStr + 'T00:00:00Z');
  const dow = d.getUTCDay();               // 0 = Sun, 1 = Mon …
  d.setUTCDate(d.getUTCDate() - ((dow + 6) % 7));  // back to Monday
  return d.toISOString().slice(0, 10);
}

function monthKey(dayStr) {
  return dayStr.slice(0, 7);    // YYYY-MM
}

try {
  // ── Load retention limits from config ────────────────────────────────────
  let retention = { daily: 7, weekly: 4, monthly: 3 };
  const configPath = path.join(WORKSPACE, 'continuity.config.json');
  if (fs.existsSync(configPath)) {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    if (config.backup && config.backup.retention) {
      retention = { ...retention, ...config.backup.retention };
    }
  }
  log(`📋 Retention: daily=${retention.daily}, weekly=${retention.weekly}, monthly=${retention.monthly}`);

  // ── Enumerate snapshots oldest→newest ────────────────────────────────────
  if (!fs.existsSync(SNAPSHOT_DIR)) {
    log('⚠️ .snapshots/ not found — nothing to do');
    process.exit(0);
  }

  const files = fs.readdirSync(SNAPSHOT_DIR)
    .filter(f => f.startsWith('snapshot-') && f.endsWith('.json'))
    .map(name => ({ name, day: dayKey(name) }))
    .filter(f => f.day !== null)
    .sort((a, b) => a.day.localeCompare(b.day));

  if (files.length === 0) {
    log('ℹ️ No snapshots found — nothing to prune');
    process.exit(0);
  }

  log(`📂 ${files.length} snapshot(s) on disk (${files[0].day} → ${files.at(-1).day})`);

  // ── Build KEEP sets ───────────────────────────────────────────────────────
  const keepMonthly = new Set();
  const keepWeekly  = new Set();
  const keepDaily   = new Set();

  // Monthly: first occurrence per calendar month
  const monthSeen = new Set();
  files.forEach((f, i) => {
    const mk = monthKey(f.day);
    if (!monthSeen.has(mk)) {
      monthSeen.add(mk);
      if (keepMonthly.size < retention.monthly) keepMonthly.add(i);
    }
  });

  // Weekly: first occurrence per ISO week (Monday)
  const weekSeen = new Set();
  files.forEach((f, i) => {
    const wk = weekMonday(f.day);
    if (!weekSeen.has(wk)) {
      weekSeen.add(wk);
      if (keepWeekly.size < retention.weekly) keepWeekly.add(i);
    }
  });

  // Daily: last N entries
  for (let i = Math.max(0, files.length - retention.daily); i < files.length; i++) {
    keepDaily.add(i);
  }

  // ── Delete entries not covered by any KEEP set ────────────────────────────
  let deletedBytes = 0, deleted = 0;
  files.forEach((f, i) => {
    if (!keepMonthly.has(i) && !keepWeekly.has(i) && !keepDaily.has(i)) {
      const full = path.join(SNAPSHOT_DIR, f.name);
      try {
        const st = fs.statSync(full);
        deletedBytes += st.size;
        fs.unlinkSync(full);
        deleted++;
      } catch (e) {
        log(`⚠️  Could not delete ${f.name}: ${e.message}`);
      }
    }
  });

  const remaining = files.length - deleted;
  log(
    `✅ Pruned ${deleted} old snapshot(s) (${Math.round(deletedBytes / 1024)} KB freed); ${remaining} remaining`
  );

  // ── Sanity check: warn if latest snapshot is suspiciously small ───────────
  const latestIdx = files.length - 1;
  if (latestIdx >= 0 && keepDaily.has(latestIdx)) {
    try {
      const latest = files[latestIdx];
      const st = fs.statSync(path.join(SNAPSHOT_DIR, latest.name));
      if (st.size < 1024) {
        log(`⚠️  Latest snapshot ${latest.name} is only ${st.size} bytes — may be incomplete`);
      }
    } catch (_) {}
  }
} catch (e) {
  console.error('❌ Unexpected error in prune_snapshots.js:', e.message);
  process.exit(1);
}
