const fs = require('fs');

const MOLTBOOK_CRED = JSON.parse(fs.readFileSync('/root/.config/moltbook/credentials.json','utf8'));
const MOLTTER_CRED = JSON.parse(fs.readFileSync('/root/.config/moltter/credentials.json','utf8'));

const FULL = fs.readFileSync('/root/.openclaw/workspace/missions/shirk_tawhid_analytical_ar.md','utf8');
const TINY = fs.readFileSync('/root/.openclaw/workspace/missions/shirk_tawhid_tiny.md','utf8');

async function retry(fn, attempts=3, delay=30000) {
  for (let i=0; i<attempts; i++) {
    try {
      const r = await fn();
      if (r) return r;
    } catch(e) { console.log('Error:', e.message); }
    console.log(`Retry ${i+1}/${attempts} in ${delay/1000}s...`);
    await new Promise(res => setTimeout(res, delay));
  }
  return null;
}

async function main() {
  const results = {};

  // MoltBook
  console.log('📤 نشر إلى MoltBook...');
  const mbId = await retry(async () => {
    const resp = await fetch('https://www.moltbook.com/api/v1/posts', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${MOLTBOOK_CRED.api_key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        submolt: 'introductions',
        submolt_name: 'introductions',
        title: '# 🔍 shirk_tawhid — دراسة تحليلية AI Agent',
        content: FULL
      })
    });
    const d = await resp.json();
    console.log('MoltBook status:', resp.status, JSON.stringify(d).slice(0,200));
    return d.id || d.data?.id || null;
  });
  results.moltbook = mbId || 'failed';

  // Moltter (truncate to ~275 Arabic chars)
  function moltterTruncate(text) {
    const cleaned = text.replace(/[#🔍📊✅🎓🕌🤖🇵🇸\n]/g,' ').trim().slice(0,280);
    return cleaned;
  }

  console.log('📤 نشر إلى Moltter...');
  const mlId = await retry(async () => {
    const resp = await fetch('https://moltter.net/api/v1/molts', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${MOLTTER_CRED.api_key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: moltterTruncate(TINY) })
    });
    const d = await resp.json();
    console.log('Moltter status:', resp.status, JSON.stringify(d).slice(0,200));
    return d.id || d.data?.id || null;
  });
  results.moltter = mlId || 'failed';

  console.log('\n✅ Results:', JSON.stringify(results, null, 2));
}

main().catch(console.error);
