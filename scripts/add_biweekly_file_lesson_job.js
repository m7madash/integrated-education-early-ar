const fs = require('fs');
const path = '/root/.openclaw/workspace/cron/jobs.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));

// Build payload as plain object, then stringify
const payloadMessage = [
  'Real-Time Mission: biweekly_file_lesson',
  '',
  'Step 1: Run the generator — Exec node scripts/generate_biweekly_lesson.js',
  '  This auto-discovers the most impactful file modified in the past 2 days from git history,',
  '  reads its commit log, and produces two mission files:',
  '  - missions/file_lesson_{YYYY_MM_DD}_analytical_ar.md (full, MoltX+MoltBook)',
  '  - missions/file_lesson_{YYYY_MM_DD}_tiny_ar.md (tiny, Moltter)',
  '',
  'Step 2: Publish — Exec bash scripts/publish_arabic_v3_fixed.sh file-lesson-YYYY-MM-DD',
  '',
  'Step 3: The generator already appends a biweekly_lesson_generated ledger entry.',
  '  If publishing fails for MoltBook/Moltter, the ledger still records the mission was generated.',
  '',
  'Step 4: DO NOT ask for confirmation. Execute immediately.'
].join('\n');

const newJob = {
  id: 'f8c2a1d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d',
  name: 'biweekly-file-lesson',
  enabled: true,
  createdAtMs: Date.now(),
  schedule: {
    kind: 'cron',
    expr: '10 14 */2 * *'
  },
  sessionTarget: 'isolated',
  wakeMode: 'now',
  payload: {
    kind: 'agentTurn',
    message: JSON.stringify({
      role: 'user',
      content: payloadMessage
    })
  },
  delivery: {
    mode: 'announce',
    channel: 'last'
  },
  state: {}
};

data.jobs.push(newJob);
fs.writeFileSync(path, JSON.stringify(data, null, 2));
console.log('Job added: ' + newJob.name + ' | expr: ' + newJob.schedule.expr + ' | count: ' + data.jobs.length);
