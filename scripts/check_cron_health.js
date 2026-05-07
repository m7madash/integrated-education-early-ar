const fs = require('fs');
const jobs = JSON.parse(fs.readFileSync('/root/.openclaw/workspace/cron/jobs.json','utf8')).jobs;
const now = new Date();
const utcMin = now.getUTCHours()*60 + now.getUTCMinutes();
console.log('=== Cron Job Health Check ===');
console.log('Current UTC time:', now.toISOString().slice(0,16));
console.log('');
jobs.filter(j=>j.enabled).forEach(j=>{
  const expr = j.schedule.expr;
  const parts = expr.split(' ');
  const minutePart = parts[0];
  let expectedMinutes = new Set();
  if (minutePart === '*') {
    for (let i=0;i<60;i++) expectedMinutes.add(i);
  } else if (minutePart.includes('/')) {
    const [base,stepStr] = minutePart.split('/');
    const step = parseInt(stepStr);
    const start = base === '*' ? 0 : parseInt(base);
    for (let i=start; i<60; i+=step) expectedMinutes.add(i);
  } else {
    minutePart.split(',').forEach(m=>{
      if (m !== '') expectedMinutes.add(parseInt(m));
    });
  }
  const currentMin = now.getUTCMinutes();
  const shouldFire = expectedMinutes.has(currentMin);
  const status = shouldFire ? '✅' : '⏳';
  console.log(`${status} ${j.name.padEnd(45)} | schedule: ${expr}`);
});
