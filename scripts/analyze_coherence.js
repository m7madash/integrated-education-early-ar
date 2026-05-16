#!/usr/bin/env node
/**
 * Coherence calculator for continuity improvement cycle
 * Analyzes last N continuity_check entries to compute average coherence
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const WINDOW = 50; // config coherenceWindow

function analyze() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) {
      console.log('COHERENCE=0.000 (no ledger)');
      process.exit(0);
    }

    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');

    const checks = [];
    for (const line of lines) {
      if (!line.startsWith('{')) continue;
      try {
        const e = JSON.parse(line);
        if (e.type === 'continuity_check' && e.ts) {
          checks.push(e);
        }
      } catch (err) {
        // skip
      }
    }

    if (checks.length === 0) {
      console.log('COHERENCE=0.000 (no checks)');
      return;
    }

    // Take last WINDOW entries
    const recent = checks.slice(-WINDOW);
    const sum = recent.reduce((acc, e) => acc + (e.coherence_score || 0), 0);
    const avg = sum / recent.length;

    // Also compute gap-based coherence
    let gapScoreSum = 0;
    let intervals = 0;
    const expectedMs = 30 * 60 * 1000;

    for (let i = recent.length - 1; i > 0; i--) {
      const curr = new Date(recent[i].ts).getTime();
      const prev = new Date(recent[i-1].ts).getTime();
      const gap = curr - prev;
      // Score: 1 if exactly 30min, decreases as deviation grows, clamped to [0,1]
      const deviation = Math.abs(gap - expectedMs) / expectedMs;
      gapScoreSum += Math.max(0, 1 - deviation);
      intervals++;
    }
    const gapCoherence = intervals > 0 ? gapScoreSum / intervals : 1;

    // Combined: 40% recorded score, 60% gap regularity
    const combined = (avg * 0.4) + (gapCoherence * 0.6);

    console.log(`COHERENCE_ANALYSIS: entries=${recent.length}/${checks.length}, score_avg=${avg.toFixed(4)}, gap_coherence=${gapCoherence.toFixed(4)}, combined=${combined.toFixed(4)}`);
    console.log(`COHERENCE=${combined.toFixed(4)}`);
  } catch (e) {
    console.error('COHERENCE_ANALYSIS_ERROR:', e.message);
    process.exit(1);
  }
}

analyze();
