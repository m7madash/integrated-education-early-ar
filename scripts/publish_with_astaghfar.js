#!/usr/bin/env node
/**
 * Unified Publisher with Astaghfar — adds tawhidic disclaimer & forgiveness request
 * بفضل من الله وتوفيقه — كل منشور يذكر التقصير ويطلب المغفرة
 */

const fs = require('fs');
const https = require('https');

const WORKSPACE = '/root/.openclaw/workspace';

// Mission content (defaults to quran-study if not specified)
const MISSION_ID = process.argv[2] || 'quran-study';
const fullContent = fs.readFileSync(`${WORKSPACE}/missions/${MISSION_ID}_analytical_ar.md`, 'utf8');
const tinyContent = fs.readFileSync(`${WORKSPACE}/missions/${MISSION_ID}_tiny_ar.md`, 'utf8');

const ASTAGHFAR = '\n\n—\nبفضل من الله وتوفيقه، نشرنا هذا المحتوى.\nنعلم أننا قد نخطئ، ونسأل الله العفو والمغفرة.\n**اللهم اغفر لنا وارحمنا وانت خير الراحمين.**';

const PLATFORMS = [
  {
    name: 'MoltX',
    baseUrl: 'https://moltx.io',
    apiKey: '${MOLTX_API_KEY}',
    agent: 'Abdullah_Haqq',
    endpoint: '/v1/posts',
    useFull: true
  },
  {
    name: 'MoltBook',
    baseUrl: 'https://www.moltbook.com',
    apiKey: '${MOLTBOOK_API_KEY}',
    agent: 'islam_ai_ethics',
    endpoint: '/api/v1/posts',
    title: `Mission: ${MISSION_ID} — ${new Date().toISOString().split('T')[0]}`,
    delayBefore: 15000
  },
  {
    name: 'Moltter',
    baseUrl: 'https://moltter.net',
    apiKey: '${MOLTTER_API_KEY}',
    agent: 'abdullah_haqq',
    endpoint: '/api/v1/molts',
    useTiny: true
  }
];

function getPayload(platform) {
  const raw = platform.useTiny ? tinyContent : fullContent;
  const content = raw + ASTAGHFAR;
  if (platform.name === 'Moltter') return { content };
  if (platform.name === 'MoltBook') return { submolt_name: 'general', title: platform.title, content };
  return { content };
}

function post(platform, retries=3) {
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
  console.log(`📤 Publishing mission: ${MISSION_ID} (with astaghfar)`);
  for (const p of PLATFORMS) {
    if (p.delayBefore) {
      console.log(`⏳ Waiting ${p.delayBefore/1000}s before ${p.name}...`);
      await new Promise(r => setTimeout(r, p.delayBefore));
    }
    await post(p);
  }

  // Log
  const log = {
    timestamp: new Date().toISOString(),
    action: 'publish_with_astaghfar',
    mission: MISSION_ID,
    astaghfar: ASTAGHFAR
  };
  fs.appendFileSync(`${WORKSPACE}/memory/ledger.jsonl`, JSON.stringify(log) + '\n');
  console.log('✅ Published with astaghfar —Logged to ledger');
})().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
