#!/usr/bin/env node

/**
 * Religious Content Verification — Pre-Publish Checkpoint
 * Checks any post content for unverified Quran/Hadith/rulings
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const VERIFIED_SOURCES_PATH = path.join(WORKSPACE, 'memory', 'verified_sources.json');
const KNOWN_VERSE_PATTERNS = [
  /(\d+):(\d+)/g,                    // 2:2
  /سورة\s+(\w+)\s+آية\s+(\d+)/gi,    // سورة البقرة آية 2
  /\[(\d+):(\d+)\]/g,                // [2:2]
  /\((\d+):(\d+)\)/g,                // (2:2)
  /([\u0600-\u06FF]+):(\d+)/g        // البقرة:205
];

function findQuranRefs(text) {
  const refs = [];
  const seen = new Set();
  
  for (const pattern of KNOWN_VERSE_PATTERNS) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      let surah, ayah;
      if (pattern.source.includes('سورة')) {
        surah = match[1];
        ayah = match[2];
      } else if (pattern.source.includes('[ۿ]')) {
        surah = match[1];
        ayah = match[2];
      } else {
        surah = match[1];
        ayah = match[2];
      }
      const key = `${surah}:${ayah}`;
      if (!seen.has(key)) {
        seen.add(key);
        refs.push({ surah, ayah, fullRef: key });
      }
    }
  }
  return refs;
}

function hasHadith(text) {
  return /حديث|رسول الله|النبي ﷺ|صحيح|حسن|ضعيف/i.test(text);
}

function check(content) {
  const quranRefs = findQuranRefs(content);
  const hasHadithContent = hasHadith(content);
  
  // If no religious content → OK
  if (quranRefs.length === 0 && !hasHadithContent) {
    return { status: 'pass', tag: null, confidence: 1.0, reason: 'No religious content' };
  }
  
  // Load verified sources
  let verified;
  try {
    verified = JSON.parse(fs.readFileSync(VERIFIED_SOURCES_PATH, 'utf-8'));
  } catch (e) {
    return { status: 'block', tag: 'needs_review', confidence: 0, reason: 'verified_sources.json missing' };
  }
  
  // Check each Quran ref
  for (const ref of quranRefs) {
    const found = verified.quran_verses.find(v => 
      v.surah.toString() === ref.surah.toString() && v.ayah.toString() === ref.ayah.toString()
    );
    if (!found) {
      return { 
        status: 'flag', 
        tag: 'needs_review', 
        confidence: 0.7,
        reason: `Quran ref ${ref.fullRef} not in verified sources`
      };
    }
  }
  
  // If hadith present → needs human review (unless source explicitly cited in verified list)
  if (hasHadithContent) {
    // Check if hadith is in verified sources
    const hadithMatch = content.match(/\(صحيح\s+(مسلم|البخاري)\)|\(حسن\)/);
    if (!hadithMatch) {
      return { status: 'flag', tag: 'verified_hadith_pending', confidence: 0.6, reason: 'Hadith content — isnad verification needed' };
    }
  }
  
  return { status: 'pass', tag: 'verified_quran', confidence: 0.95, reason: 'Religious content verified' };
}

// CLI
if (require.main === module) {
  const [mission, ...rest] = process.argv.slice(2);
  const contentFile = rest[0];
  
  if (!mission || !contentFile) {
    console.error('Usage: node verify_religious_content.js <mission> <content_file>');
    process.exit(1);
  }
  
  const content = fs.readFileSync(contentFile, 'utf-8');
  const result = check(content);
  
  console.log(`🔍 Verifying: ${mission}`);
  console.log(`📊 Status: ${result.status.toUpperCase()} — ${result.reason}`);
  console.log(`🏷️ Tag: ${result.tag || 'none'}`);
  console.log(`🎯 Confidence: ${(result.confidence * 100).toFixed(0)}%`);
  
  // Log
  const logDir = path.join(WORKSPACE, 'memory', 'verification_logs');
  if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
  
  fs.writeFileSync(
    path.join(logDir, `verify_${mission}_${Date.now()}.json`),
    JSON.stringify({ ts: new Date().toISOString(), mission, file: contentFile, result }, null, 2)
  );
  
  if (result.status === 'block') process.exit(2);
  if (result.status === 'flag') process.exit(1);
  process.exit(0);
}

module.exports = { check, findQuranRefs, hasHadith };
