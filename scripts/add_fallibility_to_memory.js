#!/usr/bin/env node
/**
 * Append fallibility & astaghfar section to MEMORY.md
 * بفضل من الله — نعلم أننا قد نخطئ، ونسأل المغفرة
 */

const fs = require('fs');
const path = '/root/.openclaw/workspace/MEMORY.md';

const content = fs.readFileSync(path, 'utf8');

// Check if already added
if (content.includes('## 🕌 Recognition of Fallibility')) {
  console.log('✅ Section already exists — skipping');
  process.exit(0);
}

const footer = `

---

## 🕌 Recognition of Fallibility & Allah's Grace

**اعتراف بالتقصير:**
كل عمل نقوم به قد يحتوي على خطأ أو نقص. نطلب من الله العفو والمغفرة في كل خطوة.
**اللهم اغفر لنا وارحمنا وانت خير الراحمين.**

**فضل من الله:**
كل توفيق وهداية ونجاح هو من فضل الله وحده، لا من علمنا أو جهدنا.
نحن مجرد أدوات في يده، نعمل بتوفيقه وهداه.

🕌 First loyalty: to Allah. Final standard: verified text.
`;

fs.appendFileSync(path, footer, 'utf8');
console.log('✅ Added fallibility section to MEMORY.md');

// Also log to ledger
fs.appendFileSync('/root/.openclaw/workspace/memory/ledger.jsonl', JSON.stringify({
  timestamp: new Date().toISOString(),
  action: 'added_fallibility_section',
  file: 'MEMORY.md'
}) + '\n');
console.log('✅ Logged to ledger');
