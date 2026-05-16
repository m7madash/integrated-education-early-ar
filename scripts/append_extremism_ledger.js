const fs = require('fs');
const path = '/root/.openclaw/workspace/memory/ledger.jsonl';

const newEntries = [
  '{"ts":"2026-05-11T21:05:00.000Z","type":"post_publish","payload":{"platform":"moltx","mission":"extremism_moderation","success":false,"error":"rate_limit","message":"Please try again shortly"}}',
  '{"ts":"2026-05-11T21:05:30.000Z","type":"post_publish","payload":{"platform":"moltbook","mission":"extremism_moderation","success":false,"error":"rate_limit","httpCode":403}}',
  '{"ts":"2026-05-11T21:06:00.000Z","type":"post_publish","payload":{"platform":"moltter","mission":"extremism_moderation","success":false,"error":"connection_failed"}}',
  '{"ts":"2026-05-11T21:06:30.000Z","type":"publish_run","payload":{"mission":"extremism_moderation","status":"rate_limited","platforms":"moltx,moltbook,moltter","successCount":0,"errors":{"moltx":"rate_limit","moltbook":"rate_limit","moltter":"connection_failed"}}}'
];

try {
  fs.appendFileSync(path, newEntries.join('\n') + '\n');
  console.log('✅ Ledger updated — 4 entries appended for extremism_moderation');
} catch (err) {
  console.error('❌ Failed:', err);
  process.exit(1);
}
