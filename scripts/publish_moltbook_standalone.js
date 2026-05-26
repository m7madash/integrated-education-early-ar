#!/usr/bin/env node
/**
 * MoltBook Publisher — standalone helper
 * Reads content from stdin, posts to MoltBook API
 * v2: uses body as-is (no double-stringify), proper Content-Length
 *
 * Usage: cat content.md | node publish_moltbook_standalone.js <mission-key>
 * Example: cat file.md | node publish_moltbook_standalone.js shirk-tawhid
 */

const fs = require('fs');
const https = require('https');
const os = require('os');

const CRED_PATH = os.homedir() + '/.config/moltbook/credentials.json';
const API_BASE = 'https://www.moltbook.com/api/v1';
const SUBMOLT_ID = '29beb7ee-ca7d-4290-9c2f-09926264866f';

// Read content from stdin
const chunks = [];
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { chunks.push(chunk); });
process.stdin.on('end', () => {
  const content = chunks.join('');
  if (!content.trim()) { console.error('No content on stdin'); process.exit(1); }
  run(content, process.argv[2] || 'mission');
});
process.stdin.on('error', e => { console.error('stdin error:', e.message); process.exit(1); });

function ts() { return new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC'; }

function run(content, missionArg) {
  // Load credentials
  let apiKey;
  try {
    const cred = JSON.parse(fs.readFileSync(CRED_PATH, 'utf8'));
    apiKey = cred.api_key;
  } catch(e) {
    console.error('Cannot read MoltBook credentials:', e.message);
    process.exit(1);
  }
  if (!apiKey) { console.error('api_key missing from', CRED_PATH); process.exit(1); }

  const title = missionArg.split('-').map(w =>
    w.charAt(0).toUpperCase() + w.slice(1)
  ).join(' ') + ' — دراسة تحليلية AI Agent';

  // Build body
  const body = JSON.stringify({ title, content, submolt_id: SUBMOLT_ID });
  const bodyBytes = Buffer.byteLength(body);

  // Post via HTTPS directly (avoids shell escaping entirely)
  const req = https.request(API_BASE + '/posts', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + apiKey,
      'Content-Type': 'application/json',
      'Content-Length': bodyBytes
    }
  }, res => {
    let data = '';
    res.on('data', chunk => { data += chunk; });
    res.on('end', () => {
      console.log('ts:', ts());
      console.log('status:', res.statusCode);
      console.log('response:', data.slice(0, 400));
      let id;
      try { const j = JSON.parse(data); id = j.data?.id || j.id; } catch(_) {}
      if (res.statusCode >= 200 && res.statusCode < 300) {
        console.log('id:', id || 'unknown');
        process.exit(0);
      } else {
        console.error('MoltBook POST failed:', res.statusCode, data.slice(0, 200));
        process.exit(1);
      }
    });
  });

  req.on('error', e => { console.error('Request error:', e.message); process.exit(1); });
  req.write(body);
  req.end();
}
