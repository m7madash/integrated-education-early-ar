#!/usr/bin/env node
// Update cron reference file to use evolution files
const fs = require('fs');
const path = require('path');

const REF_FILE = '/root/.openclaw/workspace/cron/jobs.json';

const updates = {
    'spiritual-morning': {
        new_file: '/root/.openclaw/workspace/missions/spiritual-morning_evolution.md',
        new_pub: 'spiritual-morning-evolution'
    },
    'dhikr-evening-combined': {
        new_file: '/root/.openclaw/workspace/missions/dhikr-evening_evolution.md',
        new_pub: 'dhikr-evening-evolution'
    },
    'injustice-justice-combined': {
        new_file: '/root/.openclaw/workspace/missions/injustice-justice_evolution.md',
        new_pub: 'injustice-justice-evolution'
    },
    'wisdom-day-combined': {
        new_file: '/root/.openclaw/workspace/missions/wisdom-knowledge_evolution.md',
        new_pub: 'wisdom-knowledge-evolution'
    },
    'health-peace-combined': {
        new_file: '/root/.openclaw/workspace/missions/war-peace_evolution.md',
        new_pub: 'war-peace'
    },
    'shirk-tawhid-combined': {
        new_file: '/root/.openclaw/workspace/missions/shirk-tawhid_evolution.md',
        new_pub: 'shirk-tawhid-evolution'
    },
    'health-extremism-combined': {
        new_file: '/root/.openclaw/workspace/missions/extremism-moderation_evolution.md',
        new_pub: 'extremism-moderation'
    },
    'corruption-slavery-combined': {
        new_file: '/root/.openclaw/workspace/missions/corruption-slavery_evolution.md',
        new_pub: 'corruption-slavery'
    }
};

const TEMPLATE = '🕌 Evolution Mission: {name}\n\nRead the evolution mission file and publish.\n\n1. Read: {file_path}\n2. Publish: Exec node scripts/combined_publisher.js {script_arg}\n3. Log: Ledger auto-written by publisher.\n4. DO NOT ask for confirmation. Execute immediately.';

const data = JSON.parse(fs.readFileSync(REF_FILE, 'utf8'));
let updated = 0;

for (const job of data) {
    const name = job.name;
    if (!updates[name]) continue;
    const info = updates[name];
    const content = TEMPLATE.replace('{name}', name).replace('{file_path}', info.new_file).replace('{script_arg}', info.new_pub);
    job.payload.message = JSON.stringify({ role: 'user', content });
    updated++;
    console.log('✅', name, '→', info.new_file);
}

fs.writeFileSync(REF_FILE, JSON.stringify(data, null, 2));
console.log('Total updated reference file:', updated);
