#!/usr/bin/env node
/**
 * Coherence check wrapper — single binary for exec preflight compliance
 * Calculates coherence based on recent continuity_check entries
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const COHERENCE_WINDOW = 50; // entries to consider

function calculateCoherence() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) {
      console.log('COHERENCE=0.000 (no ledger)');
      return;
    }

    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');

    // Extract continuity_check entries with timestamps
    const checks = [];
    for (const line of lines) {
      if (!line.startsWith('{')) continue;
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'continuity_check' && entry.ts) {
          checks.push({
            ts: new Date(entry.ts).getTime(),
            coherence_ok: entry.coherence_ok,
            coherence_score: entry.coherence_score
          });
        }
      } catch (e) {
        // skip malformed
      }
    }

    if (checks.length === 0) {
      console.log('COHERENCE=0.000 (no checks found)');
      return;
    }

    // Sort by timestamp descending (newest first)
    checks.sort((a, b) => b.ts - a.ts);

    // Take recent window
    const recent = checks.slice(0, COHERENCE_WINDOW);

    // Calculate average interval coherence
    let totalGapScore = 0;
    let intervals = 0;

    const expectedIntervalMs = 30 * 60 * 1000; // 30 minutes

    for (let i = 0; i < recent.length - 1; i++) {
      const gapMs = recent[i].ts - recent[i+1].ts;
      const gapScore = Math.max(0, 1 - Math.abs(gapMs - expectedIntervalMs) / expectedIntervalMs);
      totalGapScore += gapScore;
      intervals++;
    }

    const intervalCoherence = intervals > 0 ? totalGapScore / intervals : 1;

    // Factor in explicit coherence scores if present
    const scoredEntries = recent.filter(e => e.coherence_score !== undefined);
    let scoreCoherence = 1;
    if (scoredEntries.length > 0) {
      const sumScores = scoredEntries.reduce((acc, e) => acc + e.coherence_score, 0);
      scoreCoherence = sumScores / scoredEntries.length;
    }

    // Combined coherence: 60% interval regularity, 40% recorded scores
    const combined = (intervalCoherence * 0.6) + (scoreCoherence * 0.4);

    console.log(`COHERENCE=${combined.toFixed(4)} (window=${recent.length}/${checks.length}, intervals=${intervals})`);
  } catch (e) {
    console.error('COHERENCE_CALC_ERROR:', e.message);
    process.exit(1);
  }
}

calculateCoherence();
