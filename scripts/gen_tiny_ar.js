const fs = require('fs');
const full = fs.readFileSync('/root/.openclaw/workspace/missions/ignorance_knowledge_analytical_ar.md', 'utf8');
const text = full
  .replace(/[#*`>\[\]|]/g, ' ')
  .replace(/\s+/g, ' ').trim();
const tiny = text.slice(0, 275);
const outPath = '/root/.openclaw/workspace/missions/ignorance_knowledge_tiny_analytical_ar.md';
fs.writeFileSync(outPath, tiny, 'utf8');
console.log('Written tiny version (' + tiny.length + ' chars)');
