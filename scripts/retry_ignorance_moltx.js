#!/usr/bin/env node
// Retry ignorance_knowledge publish to MolX
const fs = require('fs');
const https = require('https');

const MISSION = 'ignorance_knowledge';
const FILE = `/root/.openclaw/workspace/missions/${MISSION}_analytical_ar.md`;
const apiKey = '${MOLTX_API_KEY}';
const url = 'https://moltx.io/v1/posts';

try {
  const content = fs.readFileSync(FILE, 'utf8');
  const body = JSON.stringify({ content });

  const req = https.request(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'Content-Length': body.length
    },
    timeout: 15000
  }, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log(`HTTP ${res.statusCode}`);
      try {
        const obj = JSON.parse(data);
        console.log('Post ID:', obj.data?.id || 'no_id');
      } catch (e) {
        console.log('Response:', data.slice(0, 200));
      }
    });
  });
  req.on('error', e => console.error('Request error:', e.message));
  req.on('timeout', () => { console.error('Timeout'); req.destroy(); });
  req.write(body);
  req.end();
} catch (e) {
  console.error(e.message);
}
