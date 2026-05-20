const fs = require('fs');
const path = '/root/.openclaw/workspace/cron/jobs.json';
const data = JSON.parse(fs.readFileSync(path, 'utf8'));

const newJob = {
  id: 'd7e03f1a-0b4c-47a2-9e8d-1f2a3b4c5d6e',
  name: 'learning-journey-biweekly',
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
      content: 'Real-Time Mission: learning_journey_biweekly\n\nExecute autonomously:\n\n1. Read pre-written files:\n   - Full: /root/.openclaw/workspace/missions/learning_journey_biweekly_analytical_ar.md\n   - Tiny: /root/.openclaw/workspace/missions/learning_journey_biweekly_moltter.md\n\n2. Publish: Exec bash scripts/publish_arabic_v3_fixed.sh learning_journey_biweekly\n\n3. Log: Append to memory/ledger.jsonl entry with platform IDs and status.\n\n4. DO NOT ask for confirmation. Execute immediately.'
    })
  },
  delivery: {
    mode: 'announce',
    channel: 'last'
  },
  state: {}
};

// Check for id/name collision
const exists = data.jobs.some(j => j.id === newJob.id || j.name === newJob.name);
if (exists) {
  console.log('Job already exists, skipping');
  process.exit(0);
}

data.jobs.push(newJob);
fs.writeFileSync(path, JSON.stringify(data, null, 2));
console.log('Job added: ' + newJob.name + ' | expr: ' + newJob.schedule.expr + ' | count: ' + data.jobs.length);
