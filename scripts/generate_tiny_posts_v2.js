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

function extractTitle(content) {
  // First line: "# 🔍 ... — دراسة تحليلية AI Agent"
  const m = content.match(/^#\s+(🔍.*?)\s*—/);
  if (m) return m[1].trim();
  // fallback: first line without the comment
  return content.split('\n')[0].replace(/^#\s+/, '').trim();
}

function extractFirstBullet(content, marker) {
  const idx = content.indexOf(marker);
  if (idx === -1) return '';
  const after = content.slice(idx + marker.length);
  const lines = after.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('- ')) {
      return trimmed.substring(2).replace(/\s+/g, ' ');
    }
  }
  return '';
}

function extractQuranRef(content) {
  // Find line with "الآية:**Surah:Verse**"
  const re = /الآية:\s*\*\*([^*]+?)\*\*/;
  const m = content.match(re);
  if (m) return m[1].trim();
  // fallback: find "الآية: **" then take until dash
  const m2 = content.match(/الآية:\s*\*\*([^—]+)/);
  if (m2) return m2[1].trim();
  return '';
}

function condense(text, max) {
  if (!text) return '';
  // Remove source parentheses
  let t = text.replace(/\s*\([^)]*\)/g, '');
  if (t.length > max) {
    t = t.substring(0, max - 3) + '...';
  }
  return t;
}

missions.forEach(base => {
  const file = path.join(MISSIONS_DIR, `${base}_analytical_ar.md`);
  if (!fs.existsSync(file)) {
    console.log(`❌ missing ${base}`);
    return;
  }
  const content = fs.readFileSync(file, 'utf8');
  const title = extractTitle(content);
  const stat = extractFirstBullet(content, '## 📊');
  const app = extractFirstBullet(content, '## 💡') || 'تطبيق النهج';
  const quran = extractQuranRef(content);

  // Build tiny content
  // Format: 🔍<title>: <stat>. الحل: <app> [القرآن: <quran>] #hashtag
  // We'll use first hashtag from final line.
  const finalLine = content.trim().split('\n').pop();
  const hashtagsMatch = finalLine.match(/(#\S+(?:\s+#\S+)*)/);
  let hashtags = hashtagsMatch ? hashtagsMatch[1] : `#${base.replace(/-/g, '_')}`;

  // Keep only first two hashtags to save space
  const tagsArray = hashtags.split(/\s+/).slice(0, 2);
  hashtags = tagsArray.join(' ');

  let tiny = `🔍${title}: ${condense(stat, 80)}. الحل: ${condense(app, 60)}`;
  if (quran) tiny += `. القرآن: ${quran}`;
  tiny += ` ${hashtags}`;

  // Ensure <= 280
  if (tiny.length > 280) {
    // Further truncate app part
    const idx = tiny.indexOf('. الحل:');
    if (idx !== -1) {
      const prefix = tiny.slice(0, idx);
      const suffix = tiny.slice(idx);
      const maxSuffix = 280 - prefix.length - 1; // minus dot space
      if (suffix.length > maxSuffix) {
        tiny = prefix + '. ' + suffix.slice(0, maxSuffix-2) + '..';
      }
    } else {
      tiny = tiny.substring(0, 277) + '...';
    }
  }

  const outPath = path.join(MISSIONS_DIR, `${base}_tiny_ar.md`);
  fs.writeFileSync(outPath, tiny, 'utf8');
  const len = tiny.length;
  const status = len <= 280 ? '✅' : `❌${len}`;
  console.log(`${status} ${base} → ${len} chars`);
  console.log(`   ${tiny}`);
  console.log();
});

console.log('✅ All tiny posts generated.');
