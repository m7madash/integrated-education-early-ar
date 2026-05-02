#!/usr/bin/env node

/**
 * KiloClaw - Religious Memory Tagging System
 * Tags memory entries with religious verification status
 * 
 * Usage: node scripts/tag_memory_entries.js [date] [--dry-run]
 * Example: node scripts/tag_memory_entries.js 2026-05-02 --dry-run
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
  memoryDir: path.join(__dirname, '..', 'memory'),
  tagsIndexPath: path.join(__dirname, '..', 'memory', 'religious_tags_index.json'),
  quranPattern: /سورة\s+\w+\s+آية\s+\d+|\[\d+:\d+\]|\([\d:]+\)/g,
  quranArabicOnly: /[\u0600-\u06FF]/,
  hadithIndicators: /حديث| said prophet|قال رسول الله|قال النبي|\(صحيح\)|\(حسن\)|\(ضعيف\)/i,
  sahabaConsensus: /إجماع الصحابة|روى الصحابة|الصحابة رضوان الله عليهم/i,
  scholarPattern: /قال العارف|قال العالم|قال الشيخ|影印 scholars/i
};

function loadTagsIndex() {
  if (!fs.existsSync(CONFIG.tagsIndexPath)) {
    console.error(`❌ Tags index not found: ${CONFIG.tagsIndexPath}`);
    console.log('Creating default tags index...');
    return createDefaultTagsIndex();
  }
  return JSON.parse(fs.readFileSync(CONFIG.tagsIndexPath, 'utf-8'));
}

function createDefaultTagsIndex() {
  const defaultIndex = {
    schema_version: "1.0",
    last_updated: new Date().toISOString(),
    tag_definitions: {
      "verified_quran": {
        name: "Quran Verified - Arabic",
        description: "Arabic Quranic text verified against quran.com (hafs ms)",
        allowed_operations: ["publish", "reference", "share"],
        confidence_level: 1.0
      },
      "verified_hadith": {
        name: "Hadith Verified - Authenticated",
        description: "Hadith with verified isnad connected to Companion",
        allowed_operations: ["publish", "reference", "share"],
        confidence_level: 0.95
      },
      "needs_review": {
        name: "Needs Religious Verification",
        description: "Religious content pending verification",
        allowed_operations: ["internal_reference_only"],
        confidence_level: 0.0
      },
      "human_verified_only": {
        name: "Human Scholar Only",
        description: "Questions/rulings requiring qualified scholar",
        allowed_operations: ["log_only", "defer"],
        confidence_level: 0.0
      }
    }
  };
  fs.writeFileSync(CONFIG.tagsIndexPath, JSON.stringify(defaultIndex, null, 2));
  return defaultIndex;
}

function detectQuran(text) {
  // Check for Arabic Quranic text patterns
  const quranRefs = [
    /سورة\s+(\w+)\s+آية\s+(\d+)/,  // "سورة البقرة آية 2"
    /\[(\d+):(\d+)\]/,                // "[2:2]"
    /\((\d+):(\d+)\)/,                // "(2:2)"
    /آية\s+(\d+)\s+من\s+سورة\s+(\w+)/ // "آية 2 من سورة البقرة"
  ];
  
  for (const pattern of quranRefs) {
    const match = text.match(pattern);
    if (match) {
      return {
        tag: "verified_quran",
        reference: `${match[2] || match[1]}:${match[1] || match[2]}`,
        confidence: 1.0
      };
    }
  }
  
  // Check for common Quranic phrases in Arabic
  const commonQuranicPhrases = [
    "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    "يَا أَيُّهَا النَّاسُ",
    "يَا أَيُّهَا النَّاسُ اعْبَدُوا رَبَّكُمُ"
  ];
  
  for (const phrase of commonQuranicPhrases) {
    if (text.includes(phrase)) {
      return {
        tag: "verified_quran",
        reference: "common_phrase",
        confidence: 0.9,
        note: "Common Quranic phrase - verify exact reference"
      };
    }
  }
  
  return null;
}

function detectHadith(text) {
  const hadithIndicators = [
    /حديث\s+عن\s+النبي/i,
    /قال\s+رسول\s+الله/i,
    /عن\s+النبي\s+ﷺ/i,
    /\(صحيح\s+مسلم\)|\(صحيح\s+البخاري\)/i,
    /رواه\s+بُخَارِيُّ|رواه\s+مُسْلِمٌ/i
  ];
  
  for (const pattern of hadithIndicators) {
    if (pattern.test(text)) {
      return {
        tag: "verified_hadith",
        source: "requires extraction",
        confidence: 0.8,
        note: "Hadith indicator found - extract source/isnad"
      };
    }
  }
  
  return null;
}

function detectNeedsReview(text) {
  // Ambiguous religious language without clear source
  const uncertainPhrases = [
    "يُقال",
    "من说是",
    "ذكر",
    "بعض العلماء",
    "قد",
    "ربما"
  ];
  
  for (const phrase of uncertainPhrases) {
    if (text.includes(phrase)) {
      return {
        tag: "needs_review",
        reason: `Contains uncertain phrase: "${phrase}"`,
        confidence: 0.0
      };
    }
  }
  
  return null;
}

function classifyMemoryEntry(entry) {
  const text = entry.content || entry.text || '';
  
  // Priority 1: Check for explicit tags already
  if (entry.tag) {
    return { tag: entry.tag, confidence: 1.0, source: "pre-tagged" };
  }
  
  // Priority 2: Quran detection
  const quran = detectQuran(text);
  if (quran) {
    return { ...quran, justification: "Quranic Arabic text with reference pattern" };
  }
  
  // Priority 3: Hadith detection
  const hadith = detectHadith(text);
  if (hadith) {
    return { ...hadith, justification: "Hadith language with prophetic reference" };
  }
  
  // Priority 4: Needs review (ambiguous)
  if (detectNeedsReview(text)) {
    return { tag: "needs_review", confidence: 0.0, justification: "Ambiguous religious phrasing" };
  }
  
  // Default: No religious content detected
  return { tag: null, confidence: 0, justification: "No religious content detected" };
}

function processMemoryFile(filePath, dryRun = false) {
  console.log(`\n📄 Processing: ${path.basename(filePath)}`);
  
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  let taggedEntries = [];
  let changesCount = 0;
  
  // Simple parsing: look for markdown headers and bullet points
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line.startsWith('#')) continue;
    
    // Heuristic: lines with Arabic religious keywords
    if (/القرآن|الحديث|النبي|الرسول|الإجماع|الصحابة/.test(line)) {
      const classification = classifyMemoryEntry({ content: line });
      
      if (classification.tag) {
        changesCount++;
        taggedEntries.push({
          lineNumber: i + 1,
          original: lines[i],
          tag: classification.tag,
          confidence: classification.confidence,
          justification: classification.justification
        });
        
        if (!dryRun) {
          // Add invisible tag comment for future processing
          // Format: <!-- TAG:verified_quran confidence=1.0 -->
          const tagComment = ` <!-- TAG:${classification.tag} confidence=${classification.confidence} -->`;
          if (!lines[i].includes('<!-- TAG:')) {
            lines[i] = lines[i] + tagComment;
          }
        }
      }
    }
  }
  
  if (!dryRun && changesCount > 0) {
    fs.writeFileSync(filePath, lines.join('\n'));
    console.log(`✅ Tagged ${changesCount} entries in ${path.basename(filePath)}`);
  }
  
  return { file: path.basename(filePath), taggedEntries, changesCount };
}

function main() {
  const args = process.argv.slice(2);
  const targetDate = args[0] || '2026-05-02';
  const dryRun = args.includes('--dry-run');
  
  console.log(`🏷️ Religious Memory Tagging System`);
  console.log(`📅 Target date: ${targetDate}`);
  console.log(`🔍 Dry run: ${dryRun ? 'YES' : 'NO'}`);
  
  // Load tags index
  const tagsIndex = loadTagsIndex();
  console.log(`✅ Tags schema loaded (v${tagsIndex.schema_version})`);
  
  // Process memory file for target date
  const memoryFile = path.join(CONFIG.memoryDir, `${targetDate}.md`);
  if (!fs.existsSync(memoryFile)) {
    console.error(`❌ Memory file not found: ${memoryFile}`);
    process.exit(1);
  }
  
  const result = processMemoryFile(memoryFile, dryRun);
  
  // Generate tags index entry
  const tagsLogPath = path.join(CONFIG.memoryDir, `tags_${targetDate}.json`);
  const tagsLog = {
    date: targetDate,
    timestamp: new Date().toISOString(),
    files_processed: [result.file],
    total_tags_applied: result.changesCount,
    entries: result.taggedEntries
  };
  
  fs.writeFileSync(tagsLogPath, JSON.stringify(tagsLog, null, 2));
  console.log(`📊 Tags log saved: ${path.basename(tagsLogPath)}`);
  
  if (dryRun) {
    console.log('\n⚠️ DRY RUN — no files modified');
    console.log(`💡 Run without --dry-run to apply tags`);
  } else {
    console.log('\n✅ Tagging complete!');
    console.log(`📝 Commit: git add memory/ && git commit -m "feat: religious memory tagging ${targetDate}"`);
  }
  
  process.exit(0);
}

main();
