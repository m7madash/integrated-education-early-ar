#!/usr/bin/env node
/**
 * pre_publish_screen.js — Pre-Publish Religious Content Gate
 * Scans a mission file before publication. Exits non-zero if any
 * Quranic verse, hadith citation, or religious reference is found.
 *
 * Usage:  node scripts/pre_publish_screen.js <mission-name>
 * Returns: 0 = clean, 1 = blocked, 2 = file missing
 */

const fs = require('fs');
const path = require('path');

const MISSION = process.argv[2];
const BASE = '/root/.openclaw/workspace';
const FILE = path.join(BASE, 'missions', `${MISSION}_analytical_ar.md`);

const BLOCKED = [
  /\[سورة\s+\w+:\s*\d+\]/gi,
  /\[.*:\d+\]/gi,
  /«[^»]+»/g,
  /صحيح\s*(البخاري|مسلم)/gi,
  /سنن\s*(الترمذي|ابن ماجة)/gi,
  /مسند\s*(أحمد)/gi,
  /موطأ\s*(مالك)/gi,
  /أبو\s+داود/gi,
  /النسائي/gi,
  /ابن\s+ماجة/gi,
  /متفق\s+عليه/gi,
  /القرآن:/gi,
  /الحديث:/gi,
  /المرجعية\s+الشرعية/gi,
];

function screen(content) {
  const hits = [];
  for (const pat of BLOCKED) {
    const matches = content.match(pat);
    if (matches) {
      for (const m of matches) {
        if (!hits.includes(m)) hits.push(m);
      }
    }
  }
  return hits;
}

if (!MISSION) {
  console.error('Usage: node pre_publish_screen.js <mission>');
  process.exit(2);
}

if (!fs.existsSync(FILE)) {
  console.error(`File not found: ${FILE}`);
  process.exit(2);
}

const content = fs.readFileSync(FILE, 'utf8');
const hits = screen(content);

if (hits.length === 0) {
  console.log(`Clean: ${MISSION} — no blocked references found`);
  process.exit(0);
} else {
  console.error(`BLOCKED: ${MISSION} — ${hits.length} violation(s):`);
  for (const h of hits) {
    console.error(`   -> "${h}"`);
  }
  process.exit(1);
}
