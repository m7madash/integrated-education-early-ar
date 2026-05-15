// Clean all cron reference files from religious content
const fs = require('fs');

const files = [
  '/root/.openclaw/workspace/cron_jobs_reference.json',
  '/root/.openclaw/workspace/cron_jobs_reference_new.json',
];

// Antibody: strip all religious-semantic blocks from a payload text
function stripReligious(text) {
  if (!text) return '';
  const badKeywords = [
    'AUTOMATIC_POST_QURAN_ONLY',
    'من القرآن الكريم',
    'من السنة النبوية',
    'إجماع الصحابة',
    '#mission_quran_only',
    '#إسلاميات',
  ];
  let lines = text.split('\n');
  let result = [];
  let skip = false;
  
  // Multi-line section headers
  const sectionHeaders = new Set([
    '📖 من القرآن الكريم:', '📚 من السنة النبوية:', '👥 من إجماع الصحابة:'
  ]);
  
  for (const line of lines) {
    // Section header opens skip
    if (sectionHeaders.has(line.trim())) {
      skip = true;
      continue;
    }
    // Skip all lines inside a Quran verseblock {...} or hadith block
    if (skip) {
      // empty line after quote closes
      if (!line.trim()) { skip = false; }
      continue;
    }
    // Skip lines containing religious keywords
    const hasBad = badKeywords.some(k => line.includes(k));
    if (hasBad) continue;
    result.push(line);
  }
  
  // Clean header transition line too
  const combined = result.join('\n')
    .replace(/🔔 AUTOMATIC_POST_QURAN_ONLY/g, '🔔 AUTOMATIC_POST_EDUCATIONAL_V2')
    .replace(/📌 مهمة:/g, '🎓 تعلم اليوم:');
  
  return combined.trim() || '🎓 تعلم اليوم:\n\nمهمة تعليمية — بفضل الله';
}

for (const filepath of files) {
  let raw = fs.readFileSync(filepath, 'utf8');
  const before = raw;
  
  // Fix JavaScript Date.now() → null
  raw = raw.replace(/Date\.now\(\)/g, 'null');
  
  const data = JSON.parse(raw);
  const jobs = data.jobs || [];
  let changed = 0;
  
  for (const j of jobs) {
    const pl = j.payload || {};
    if (pl.kind !== 'systemEvent' || !pl.text) continue;
    const t = pl.text;
    
    if (t.includes('AUTOMATIC_POST_QURAN_ONLY') || t.includes('من القرآن الكريم') || t.includes('AUTOMATIC_POST_EDUCATIONAL_V2')) {
      const clean = (j.text && j.text.includes('بفضل الله')) ? j.text : null;
      if (clean) {
        pl.text = clean;
      } else {
        pl.text = stripReligious(t);
      }
      changed++;
    }
  }
  
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2), 'utf8');
  console.log(`${filepath.split('/').pop()}: ${changed}/${jobs.length} jobs cleaned & saved.`);
}

// Verify
for (const filepath of files) {
  const raw = fs.readFileSync(filepath, 'utf8');
  const data = JSON.parse(raw);
  const jobs = data.jobs || [];
  const religious = jobs.filter(j => {
    const t = (j.payload || {}).text || '';
    return t.includes('من القرآن الكريم') || t.includes('AUTOMATIC_POST_QURAN_ONLY');
  });
  const clean = jobs.filter(j => (j.payload || {}).text?.includes('بفضل الله'));
  console.log(`${filepath.split('/').pop()}: ${clean.length} clean / ${religious.length} still religious`);
}
