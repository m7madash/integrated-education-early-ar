#!/usr/bin/env node
// Convert *_quran_only.md missions to cron payload format
// Usage: node convert_missions_to_cron.js

const fs = require('fs');
const path = require('path');

const missionsDir = '/root/.openclaw/workspace/missions';
const cronFile = '/root/.openclaw/workspace/cron_jobs_reference.json';

// Read all quran_only mission files
const quranOnlyFiles = fs.readdirSync(missionsDir)
  .filter(f => f.endsWith('_quran_only.md'))
  .sort();

console.log(`Found ${quranOnlyFiles.length} Quran-only mission files`);

// Function to convert mission file to payload text
function missionFileToPayload(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const filename = path.basename(filePath, '_quran_only.md');
  const missionName = filename.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  // Extract sections
  const quranMatch = content.match(/## القرآن\n([\s\S]*?)(?=\n##|$)/);
  const sunnahMatch = content.match(/## السنة\n([\s\S]*?)(?=\n##|$)/);
  const consensusMatch = content.match(/## إجماع الصحابة\n([\s\S]*?)(?=\n##|$)/);
  const goalMatch = content.match(/## الهدف\n([\s\S]*?)(?=\n##|$)/);
  const applyMatch = content.match(/## كيف تطبق\n([\s\S]*?)(?=\n##|$)/);

  const quran = quranMatch ? quranMatch[1].trim() : '';
  const sunnah = sunnahMatch ? sunnahMatch[1].trim() : '';
  const consensus = consensusMatch ? consensusMatch[1].trim() : '';
  const goal = goalMatch ? goalMatch[1].trim() : '';
  const apply = applyMatch ? applyMatch[1].trim() : '';

  // Build payload
  let payload = `🔔 AUTOMATIC_POST_QURAN_ONLY\n\n📌 مهمة: ${missionName}\n\n`;
  payload += `📖 من القرآن الكريم:\n${quran}\n\n`;
  if (sunnah) payload += `📚 من السنة النبوية:\n${sunnah}\n\n`;
  if (consensus) payload += `👥 من إجماع الصحابة:\n${consensus}\n\n`;
  if (goal) payload += `🎯 الهدف:\n${goal}\n\n`;
  if (apply) payload += `✅ كيف تطبق:\n${apply}\n\n`;
  payload += `#mission_quran_only #إسلاميات #عدل`;

  return payload;
}

// Generate mapping
const mapping = {};
quranOnlyFiles.forEach(file => {
  const filename = file.replace('_quran_only.md', '');
  const payload = missionFileToPayload(path.join(missionsDir, file));
  mapping[filename] = payload;
  console.log(`✅ ${filename} -> payload generated (${payload.length} chars)`);
});

console.log('\n📝 Mapping created. Use this mapping to update cron_jobs_reference.json');
console.log('Example: For mission-injustice-justice-00, use mapping["injustice_justice"]');

// Save mapping to file for later use
fs.writeFileSync('/root/.openclaw/workspace/mission_payloads_quran_only.json',
  JSON.stringify(mapping, null, 2));
console.log('\n✅ Mapping saved to mission_payloads_quran_only.json');
