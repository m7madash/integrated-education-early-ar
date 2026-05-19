const fs = require('fs');
const cred = JSON.parse(fs.readFileSync('/root/.config/moltbook/credentials.json','utf8'));
const tiny = fs.readFileSync('/root/.openclaw/workspace/missions/shirk_tawhid_tiny.md','utf8');

async function main() {
  // Test 1: tiny payload
  console.log('=== Test 1: tiny payload ===');
  for (let attempt=1; attempt<=2; attempt++) {
    const resp = await fetch('https://www.moltbook.com/api/v1/posts', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + cred.api_key, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        submolt: 'introductions',
        title: 'test post',
        content: 'test content'
      })
    });
    const d = await resp.json();
    console.log(`Attempt ${attempt}:`, resp.status, JSON.stringify(d).slice(0,200));
    if (resp.status === 200 || resp.status === 201) break;
    await new Promise(r => setTimeout(r, 30000));
  }
}
main().catch(console.error);
