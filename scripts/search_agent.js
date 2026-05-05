#!/usr/bin/env node
/**
 * Search Agent — fetches latest statistics for a given mission
 * Uses web_search tool via OpenClaw (Exa/Kilo proxy)
 * Output: JSON with {mission, stats: [{source, snippet, date}], keywords}
 */

const { readFile, writeFile } = require('fs');
const { execSync } = require('child_process');

const MISSION = process.argv[2];
const BASEDIR = '/root/.openclaw/workspace';

if (!MISSION) {
  console.error('Usage: search_agent.js <mission-name>');
  process.exit(1);
}

// Load search keywords
const keywordsPath = `${BASEDIR}/missions/search_keywords.json`;
let keywords;
try {
  const kwData = JSON.parse(readFileSync(keywordsPath, 'utf8'));
  keywords = kwData[MISSION] || [MISSION];
} catch (e) {
  keywords = [MISSION, 'statistics 2025', 'latest data'];
}

// Build search query (Arabic + English for best results)
const query = keywords.join(' OR ') + ' 2025 2026 latest statistics';

console.error(`🔍 Searching for: ${MISSION}`);
console.error(`   Keywords: ${keywords.join(', ')}`);

// Use OpenClaw web_search via exec (safe — single binary)
// We call openclaw web_search which uses Exa through Kilo proxy
const cmd = `openclaw web_search --query "${query}" --count 5 --type neural --contents '{"summary":true,"highlights":true}' --freshness week`;

let searchResults;
try {
  const output = execSync(cmd, { encoding: 'utf8', stdio: ['pipe','pipe','pipe'] });
  searchResults = JSON.parse(output);
} catch (e) {
  console.error('⚠️ Search failed, using fallback static data');
  searchResults = { results: [] };
}

// Extract relevant snippets
const stats = (searchResults.results || []).map(r => ({
  source: r.url || r.title || 'unknown',
  snippet: r.snippet || r.summary || '',
  date: r.date || new Date().toISOString().split('T')[0]
}));

// If no results, use fallback minimal data
if (stats.length === 0) {
  stats.push({
    source: 'fallback-static',
    snippet: 'لا توجد بيانات حديثة متاحة حالياً — يُنصح بالتحقق من المصادر الرسمية',
    date: new Date().toISOString().split('T')[0]
  });
}

const output = {
  mission: MISSION,
  timestamp: new Date().toISOString(),
  keywords,
  stats
};

console.log(JSON.stringify(output, null, 2));

// Save for later use by content generator
writeFileSync(`${BASEDIR}/memory/search_${MISSION}_${Date.now()}.json`, JSON.stringify(output, null, 2));

process.exit(0);
