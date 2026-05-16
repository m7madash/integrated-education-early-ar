#!/usr/bin/env node
/**
 * validate_gaps_v2.js — Precise continuity gap detection
 *
 * Scans the last 4 hours for every expected :00/:30 slot
 * Reports each missing slot individually (not just aggregate).
 *
 * Usage: node scripts/continuity/validate_gaps_v2.js
 * Output: JSON to stdout + summary to stderr
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..', '..');
const ledgerPath = path.join(rootDir, 'memory', 'ledger.jsonl');

function loadLedger() {
  if (!fs.existsSync(ledgerPath)) return [];
  const lines = fs.readFileSync(ledgerPath, 'utf8').trim().split('\n');
  return lines
    .filter(l => l.trim())
    .map(l => {
      try {
        const entry = JSON.parse(l);
        return { ...entry, _raw: l };
      } catch (e) {
        return null;
      }
    })
    .filter(Boolean);
}

function hasEntryNear(entries, slotMs, windowMs = 5*60*1000) {
  const windowStart = slotMs - windowMs/2;
  const windowEnd = slotMs + windowMs/2;
  return entries.some(e => {
    const t = (new Date(e.ts)).getTime();
    return t >= windowStart && t <= windowEnd;
  });
}

function generateExpectedSlots(nowMs, hoursBack = 4) {
  const slots = [];
  const interval = 30 * 60 * 1000; // 30 min
  const startMs = nowMs - hoursBack * 60 * 60 * 1000;
  
  // Align to nearest :00 past
  const alignMs = Math.floor(startMs / interval) * interval;
  
  for (let t = alignMs; t <= nowMs; t += interval) {
    slots.push(t);
  }
  return slots;
}

function main() {
  const nowMs = Date.now();
  const entries = loadLedger();
  
  const expected = generateExpectedSlots(nowMs, 4);
  const missing = [];
  const present = [];
  
  for (const slotMs of expected) {
    const presentSlot = hasEntryNear(entries, slotMs, 10*60*1000); // using 10min window for robustness
    if (presentSlot) {
      present.push(slotMs);
    } else {
      const d = new Date(slotMs);
      missing.push({
        expected: d.toISOString(),
        human: d.toLocaleString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' }),
        epoch: slotMs
      });
    }
  }
  
  // Output JSON for machine consumption
  const result = {
    timestamp: new Date().toISOString(),
    windowHours: 4,
    totalExpected: expected.length,
    presentCount: present.length,
    missingCount: missing.length,
    missingSlots: missing,
    coveragePercent: Math.round((present.length / expected.length) * 100)
  };
  
  console.log(JSON.stringify(result, null, 2));
  
  // Human-readable summary to stderr
  const err = require('stream').writable;
  const summary = [];
  summary.push(`=== Continuity Gap Check (${new Date().toISOString()}) ===`);
  summary.push(`Window: last 4 hours`);
  summary.push(`Expected slots: ${expected.length}`);
  summary.push(`Present: ${present.length}`);
  summary.push(`Missing: ${missing.length} (${result.coveragePercent}% coverage)`);
  
  if (missing.length > 0) {
    summary.push('\nMissing periods:');
    missing.forEach(m => summary.push(`  - ${m.human} UTC`));
  }
  
  summary.push('');
  console.error(summary.join('\n'));

  // Record gap entry in ledger
  try {
    const ledgerEntry = {
      ts: new Date().toISOString(),
      type: 'continuity_gap',
      source: 'validate_gaps_v2',
      windowHours: 4,
      expectedSlots: expected.length,
      presentCount: present.length,
      missingCount: missing.length,
      missingPeriods: missing.map(m => m.human),
      coveragePercent: result.coveragePercent
    };
    fs.appendFileSync(ledgerPath, JSON.stringify(ledgerEntry) + '\n');
  } catch (e) {
    console.error('[validate_gaps_v2] Failed to write ledger:', e.message);
  }

  process.exit(0);
}

main();
