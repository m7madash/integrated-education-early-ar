#!/usr/bin/env node
const fs = require('fs');
const PATH = '/root/.openclaw/workspace/data/sahaba_consensus.json';
const [topic] = process.argv.slice(2);
if (!topic) { console.error('⛔ Usage: node sahaba_fetcher.js <topic>'); process.exit(1); }
const entries = JSON.parse(fs.readFileSync(PATH, 'utf8'));
const topicEntries = entries.filter(e => e.topic === topic);
if (!topicEntries.length) { console.log('⚠️ No sahaba consensus for:', topic); process.exit(0); }
topicEntries.forEach(e => {
  console.log(`${e.sahabi}: "${e.quote}" — ${e.source_book} (${e.context})`);
});
