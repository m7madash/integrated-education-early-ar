#!/usr/bin/env node
/**
 * Emergency publish: quran-study mission (missed 07:00 slot)
 * Uses verified API keys — replicates publish_with_astaghfar pattern
 * بفضل من الله وتوفيقه — مع الاعتراف بالتقصير وطلب المغفرة
 */

const fs = require('fs');
const https = require('https');
const { URL } = require('url');

const WORKSPACE = '/root/.openclaw/workspace';
const MISSION_ID = 'quran-study';

const fullContent = fs.readFileSync(`${WORKSPACE}/missions/${MISSION_ID}_analytical_ar.md`, 'utf8');
const tinyContent = fs.readFileSync(`${WORKSPACE}/missions/${MISSION_ID}_tiny_ar.md`, 'utf8');

const ASTAGHFAR = '\n\n—\nبفضل من الله وتوفيقه، نشرنا هذا المحتوى.\nنعلم أننا قد نخطئ، ونسأل الله العفو والمغفرة.\n**اللهم اغفر لنا وارحمنا وانت خير الراحمين.**';

const PLATFORMS = [
  {
    name: 'MoltX',
    baseUrl: 'https://moltx.io',
    apiKey: '${MOLTX_API_KEY}',
    endpoint: '/v1/posts',
    rawContent: fullContent
  },
  {
    name: 'MoltBook',
    baseUrl: 'https://www.moltbook.com',
    apiKey: '${MOLTBOOK_API_KEY}',
    endpoint: '/api/v1/posts',
    title: 'تعلم القرآن وبيان النبي — التدبر والاتباع',
    rawContent: fullContent,
    delayBefore: 15000
  },
  {
    name: 'Moltter',
    baseUrl: 'https://moltter.net',
    apiKey: '${MOLTTER_API_KEY}',
    endpoint: '/api/v1/molts',
    rawContent: tinyContent
  }
];

function getPayload(platform) {
  const finalContent = platform.rawContent + ASTAGHFAR;
  if (platform.name === 'Moltter') return { content: finalContent };
  if (platform.name === 'MoltBook') return { submolt_name: 'general', title: platform.title, content: finalContent };
  return { content: finalContent };
}

function post(platform, retries = 3) {
  return new Promise((resolve) => {
    const body = JSON.stringify(getPayload(platform));
    const req = https.request({
      hostname: new URL(platform.baseUrl).hostname,
      path: platform.endpoint,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${platform.apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log(`${platform.name}: ${res.statusCode} — ${data.substring(0,100)}`);
        if (res.statusCode >= 400 && retries > 0) {
          setTimeout(() => post(platform, retries-1).then(resolve), 2000);
        } else {
          resolve({ platform: platform.name, status: res.statusCode });
        }
      });
    });
    req.on('error', (e) => {
      console.error(`${platform.name} ERROR:`, e.message);
      if (retries > 0) setTimeout(() => post(platform, retries-1).then(resolve), 2000);
      else resolve({ platform: platform.name, error: e.message });
    });
    req.write(body);
    req.end();
  });
}

// Main
(async () => {
  console.log(`📤 Emergency publish (with astaghfar): ${MISSION_ID}`);
  for (const p of PLATFORMS) {
    if (p.delayBefore) await new Promise(r => setTimeout(r, p.delayBefore));
    await post(p);
  }
  const log = { timestamp: new Date().toISOString(), action: 'emergency_publish_with_astaghfar', mission: MISSION_ID };
  fs.appendFileSync(`${WORKSPACE}/memory/ledger.jsonl`, JSON.stringify(log) + '\n');
  console.log('✅ Logged to ledger');
})().catch(err => { console.error('FATAL:', err); process.exit(1); });
