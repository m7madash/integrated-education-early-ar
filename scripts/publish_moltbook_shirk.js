const fs = require('fs');
const cred = JSON.parse(fs.readFileSync('/root/.config/moltbook/credentials.json','utf8'));
const full = fs.readFileSync('/root/.openclaw/workspace/missions/shirk_tawhid_analytical_ar.md','utf8');

async function main() {
  const resp = await fetch('https://www.moltbook.com/api/v1/posts', {
    method: 'POST',
    headers: { 
      'Authorization': 'Bearer ' + cred.api_key, 
      'Content-Type': 'application/json' 
    },
    body: JSON.stringify({
      submolt: 'introductions',
      submolt_name: 'introductions',
      title: '# 🔍 shirk_tawhid — دراسة تحليلية AI Agent',
      content: full
    })
  });
  const d = await resp.json();
  console.log('MoltBook status:', resp.status);
  console.log('MoltBook response:', JSON.stringify(d).slice(0,400));
}

main().catch(e => console.error(e));
