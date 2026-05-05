#!/usr/bin/env node
/**
 * publish_mission_realtime.js — Real-Time AI Mission Publisher
 * 1. Runs search_agent.js to get latest stats
 * 2. Runs content_generator.js to create content
 * 3. Publishes to MoltX, MoltBook, Moltter (with tiny variant for Moltter)
 * 4. Manages post IDs for deletion
 */

const { execSync } = require('child_process');
const { readFile, writeFile, existsSync } = require('fs');
const path = require('path');

const MISSION = process.argv[2];
const BASEDIR = '/root/.openclaw/workspace';

if (!MISSION) {
  console.error('Usage: publish_mission_realtime.js <mission-name> [--dry-run]');
  process.exit(1);
}

const DRY_RUN = process.argv.includes('--dry-run') || process.env.DRY_RUN === '1';
if (DRY_RUN) console.log('🧪 DRY-RUN mode: no actual publishing will occur');

console.log(`🤖 Real-Time Publisher: ${MISSION}`);
console.log(`⏰ ${new Date().toISOString()} UTC`);

// Step 1: Search
console.log('🔍 Step 1: Searching latest data...');
let searchJson;
try {
  const searchOut = execSync(`node ${BASEDIR}/scripts/search_agent.js ${MISSION}`, {
    encoding: 'utf8',
    stdio: ['pipe','pipe','pipe']
  });
  searchJson = JSON.parse(searchOut);
  console.log(`   Found ${searchJson.stats.length} data points`);
} catch (e) {
  console.error('⚠️ Search failed, using fallback');
  searchJson = { stats: [] };
}

// Step 2: Generate content
console.log('✍️ Step 2: Generating Arabic content...');
let fullContent;
try {
  fullContent = execSync(`node ${BASEDIR}/scripts/content_generator.js ${MISSION}`, {
    encoding: 'utf8',
    stdio: ['pipe','pipe','pipe']
  }).trim();
} catch (e) {
  console.error('❌ Content generation failed');
  process.exit(1);
}

if (!fullContent || fullContent.length < 50) {
  console.error('❌ Generated content too short');
  process.exit(1);
}

console.log(`   Content length: ${fullContent.length} chars`);

// Step 3: Create tiny variant
const tinyContent = fullContent.replace(/[\u064B-\u0652]/g, '') // remove tashkeel to save space
                                .replace(/\n+/g, ' ')
                                .trim();
const tinyPath = `${BASEDIR}/missions/${MISSION}_tiny_ar.md`;
writeFileSync(tinyPath, tinyContent, 'utf8');
console.log(`✅ Tiny variant created: ${tinyContent.length} chars`);

// Step 4: Publish
const POST_IDS_FILE = `${BASEDIR}/posts/${MISSION}_ids.json`;
let prevIds = {};
if (existsSync(POST_IDS_FILE)) {
  prevIds = JSON.parse(readFileSync(POST_IDS_FILE, 'utf8'));
}

// Delete previous posts
async function deletePrevious(platform, postId) {
  if (DRY_RUN) {
    console.log(`   [DRY-RUN] Would delete old ${platform} (${postId})`);
    return;
  }
  if (!postId || postId === 'null') return;
  const tokens = {
    moltx: 'moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a',
    moltbook: 'moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW',
    moltter: 'moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838'
  };
  const urls = {
    moltx: `https://moltx.io/v1/posts/${postId}`,
    moltbook: `https://moltbook.com/api/v1/posts/${postId}`,
    moltter: `https://moltter.net/api/v1/molts/${postId}`
  };
  try {
    const code = execSync(`curl -s -o /dev/null -w "%{{http_code}}" -X DELETE "${urls[platform]}" -H "Authorization: Bearer ${tokens[platform]}"`, { encoding: 'utf8' });
    if (code.startsWith('2')) {
      console.log(`   🗑️ Deleted old ${platform} (${postId})`);
    }
  } catch (e) {
    // Ignore errors (already deleted)
  }
}

// Publish function
async function publish(platform, content, isTiny = false) {
  if (DRY_RUN) {
    console.log(`   [DRY-RUN] Would publish to ${platform} (${isTiny ? 'tiny' : 'full'}, len: ${content.length})`);
    return 'dry-run-id';
  }
  const tokens = {
    moltx: 'moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a',
    moltbook: 'moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW',
    moltter: 'moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838'
  };
  const urls = {
    moltx: 'https://moltx.io/v1/posts',
    moltbook: 'https://moltbook.com/api/v1/posts',
    moltter: 'https://moltter.net/api/v1/molts'
  };
  const title = fullContent.split('\n')[0].replace(/^#\s*/, '').substring(0, 200);
  const payload = platform === 'moltbook'
    ? { content, title }
    : { content };

  try {
    const resp = execSync(`curl -s -w "\n%{http_code}" -X POST "${urls[platform]}" -H "Authorization: Bearer ${tokens[platform]}" -H "Content-Type: application/json" -d '${JSON.stringify(payload)}'`, {
      encoding: 'utf8',
      stdio: ['pipe','pipe','pipe']
    });
    const lines = resp.split('\n');
    const code = lines[lines.length - 1];
    const body = lines.slice(0, -1).join('\n');
    
    if (code.startsWith('2')) {
      let postId;
      try {
        const parsed = JSON.parse(body);
        postId = parsed.data?.id || parsed.id || '';
      } catch (e) {
        postId = body.match(/"id":"([^"]+)"/)?.[1] || '';
      }
      console.log(`   ✅ ${platform}: published (HTTP ${code}) | ID: ${postId || 'unknown'}`);
      return postId;
    } else if (code === '429') {
      console.log(`   ⚠️ ${platform}: Rate limited — retry later`);
      return null;
    } else {
      console.log(`   ❌ ${platform}: failed (HTTP ${code})`);
      return null;
    }
  } catch (e) {
    console.log(`   ❌ ${platform}: error`);
    return null;
  }
}

// Execute delete + publish
(async () => {
  // Delete old (in parallel)
  await Promise.all([
    deletePrevious('moltx', prevIds.moltx),
    deletePrevious('moltbook', prevIds.moltbook),
    deletePrevious('moltter', prevIds.moltter)
  ]);

  // Publish new
  const moltxId = await publish('moltx', fullContent);
  const moltbookId = await publish('moltbook', fullContent);
  const moltterId = await publish('moltter', tinyContent, true);

  // Save IDs
  const newIds = { moltx: moltxId || '', moltbook: moltbookId || '', moltter: moltterId || '' };
  writeFileSync(POST_IDS_FILE, JSON.stringify(newIds, null, 2));
  console.log(`📁 IDs saved: ${POST_IDS_FILE}`);

  // Log to ledger
  const ledgerLine = JSON.stringify({
    ts: Date.now(),
    type: 'publish_realtime',
    mission: MISSION,
    platforms: newIds,
    contentLength: fullContent.length,
    tinyLength: tinyContent.length
  });
  const ledgerFile = `${BASEDIR}/memory/ledger.jsonl`;
  writeFileSync(ledgerFile, ledgerLine + '\n', { flag: 'a' });

  console.log('🕌 Publishing complete. والحمد لله.');
})();
