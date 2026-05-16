#!/usr/bin/env node
const fs = require('fs');
const path = '/root/.openclaw/cron/jobs.json';

const data = JSON.parse(fs.readFileSync(path, 'utf8'));

let removed = 0;
data.jobs.forEach(job => {
  if (job.sessionTarget === 'isolated' && job.delivery) {
    delete job.delivery;
    removed++;
  }
});

if (removed > 0) {
  fs.writeFileSync(path, JSON.stringify(data, null, 2) + '\n', 'utf8');
  console.log(`✅ Removed delivery from ${removed} isolated job(s)`);
} else {
  console.log('ℹ️ No isolated jobs with delivery found — already clean');
}
