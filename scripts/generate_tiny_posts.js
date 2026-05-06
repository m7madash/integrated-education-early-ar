const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const MISSIONS_DIR = path.join(WORKSPACE, 'missions');

const missions = [
  'anti_extortion',
  'corruption-reform',
  'dhikr-evening',
  'dhikr-morning',
  'disease-health',
  'division-unity',
  'extremism-moderation',
  'ignorance-knowledge',
  'injustice-justice',
  'modesty_filter',
  'pollution-cleanliness',
  'poverty-dignity',
  'quran-study',
  'shirk-tawhid',
  'slavery-freedom',
  'war-peace',
  'wise-disagreement-prophetic-way'
];

function extractFirstBullet(content, sectionHeader) {
  const parts = content.split(sectionHeader);
  if (parts.length < 2) return '';
  const after = parts[1];
  const lines = after.split('\n');
  for (const line of lines) {
    if (line.trim().startsWith('- ')) {
      return line.trim().substring(2).replace(/\s+/g, ' ');
    }
  }
  return '';
}

function extractTitle(content) {
  const match = content.match(/^#\s+(🔍.*?—.*?)$/m);
  if (match) return match[1].trim();
  return '';
}

function extractQuranRef(content) {
  // Look for the first occurrence of "الآية: **Surah:Verse**"
  const match = content.match(/الآية:\s*\*\*([^*]+)\*\*/);
  if (match) return match[1].trim();
  // fallback: look for pattern "الآية: **Something—"
  const match2 = content.match(/الآية:\s*\*\*([^—]+)/);
  if (match2) return match2[1].trim();
  return '';
}

function condenseStat(statLine) {
  // shorten to first clause before dash or parentheses
  let s = statLine;
  // Remove source parentheses
  s = s.replace(/\s*\([^)]*\)/g, '');
  // Truncate at first dash if long
  if (s.length > 100) {
    const dashIdx = s.indexOf(' — ');
    if (dashIdx > 0) s = s.substring(0, dashIdx);
  }
  // Truncate to 80 chars
  if (s.length > 80) s = s.substring(0, 77) + '...';
  return s;
}

function buildTiny(title, stat, app, quranRef, baseName) {
  // Derive hashtags from baseName (keep as is)
  const hashtag = '#' + baseName.replace(/-/g, '_');
  // Build: 🔍<title短>: <stat>. الحل: <app短>. القرآن: <quran>. #hashtag
  // Title: remove "— دراسة تحليلية AI Agent" part.
  const shortTitle = title.replace(/\s*—.*$/, '').trim();
  const shortStat = condenseStat(stat);
  const shortApp = app.length > 80 ? app.substring(0, 77) + '...' : app;
  const quranPart = quranRef ? `القرآن: ${quranRef}` : '';
  // Combine
  let content = `🔍${shortTitle}: ${shortStat}. الحل: ${shortApp}`;
  if (quranPart) content += `. ${quranPart}`;
  content += ` ${hashtag}`;
  // Ensure length <= 280 Arabic chars
  // Arabic chars roughly 2 bytes each but count characters
  const charCount = content.length;
  if (charCount > 280) {
    // further truncate app
    const overflow = charCount - 280;
    const newAppLen = Math.max(10, shortApp.length - overflow - 5);
    content = `🔍${shortTitle}: ${shortStat}. الحل: ${shortApp.substring(0, newAppLen)}...`;
    if (quranPart) content += `. ${quranPart}`;
    content += ` ${hashtag}`;
  }
  return content;
}

// Process each mission
missions.forEach(base => {
  const file = path.join(MISSIONS_DIR, `${base}_analytical_ar.md`);
  if (!fs.existsSync(file)) {
    console.log(`❌ Missing: ${base}`);
    return;
  }
  const content = fs.readFileSync(file, 'utf8');
  const title = extractTitle(content);
  const stat = extractFirstBullet(content, '## 📊');
  const app = extractFirstBullet(content, '## 💡');
  const quran = extractQuranRef(content);

  if (!title || !stat) {
    console.log(`⚠️  ${base}: missing title/stat`);
    return;
  }

  const tiny = buildTiny(title, stat, app || 'تطبيق النهج', quran, base);
  const outPath = path.join(MISSIONS_DIR, `${base}_tiny_ar.md`);
  fs.writeFileSync(outPath, tiny, 'utf8');
  const len = tiny.length;
  const status = len <= 280 ? '✅' : `❌${len}`;
  console.log(`${status} ${base} → ${len} chars`);
  console.log(`   ${tiny}`);
  console.log();
});

console.log('✅ Tiny generation complete.');
