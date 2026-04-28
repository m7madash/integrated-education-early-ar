#!/usr/bin/env node
// Test KPI tracker
const { checkKPIs } = require('/root/.openclaw/workspace/scripts/kpi_tracker');
checkKPIs().then(status => {
  console.log('KPI Status:', status);
  process.exit(status === 'ok' ? 0 : 1);
}).catch(err => {
  console.error('KPI Error:', err.message);
  process.exit(1);
});
