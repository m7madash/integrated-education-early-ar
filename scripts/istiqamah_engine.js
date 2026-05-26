// istiqamah_engine.js — Continuous Righteous Actions Engine
// Runs on cron trigger, checks daily posting streak, outputs istighfar reminder

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BASE = '/root/.openclaw/workspace';
const LEDGER = path.join(BASE, 'memory/ledger.jsonl');
const MEMORY = path.join(BASE, 'memory/2026-05-22.md'); // extended by this script if -w flag

function now() { return new Date().toISOString(); }

function getHoursUTC() { return new Date().getUTCHours(); }

function readLedgerToday() {
  if (!fs.existsSync(LEDGER)) return [];
  const today = new Date().toISOString().slice(0,10);
  const lines = fs.readFileSync(LEDGER, 'utf8').trim().split('\n');
  return lines.filter(l => {
    try { return JSON.parse(l).ts.slice(0,10) === today; }
    catch { return false; }
  });
}

function countTodayPosts() {
  const entries = readLedgerToday().filter(l => {
    try {
      const e = JSON.parse(l);
      return e.type === 'publish'; // evolution publishes only
    } catch { return false; }
  });
  return entries.length;
}

function getStreak() {
  if (!fs.existsSync(LEDGER)) return { current: 0, lastGap: 'N/A' };
  const lines = fs.readFileSync(LEDGER, 'utf8').trim().split('\n');
  const publishDays = new Set();
  lines.forEach(l => {
    try {
      const e = JSON.parse(l);
      if (e.type === 'publish') publishDays.add(e.ts.slice(0,10));
    } catch {}
  });
  // Count consecutive days ending today
  const today = new Date().toISOString().slice(0,10);
  let streak = 0;
  let d = new Date(today);
  while (true) {
    const ds = d.toISOString().slice(0,10);
    if (publishDays.has(ds)) { streak++; d.setUTCDate(d.getUTCDate() - 1); }
    else break;
  }
  return { current: streak };
}

function generateReminder(hour) {
  const reminders = [
    // 00-06
    `بفضل الله — اللهم إني أصحو على نعمتك، فاجعلها تصحبة لي اليوم كله. استغفر الله العظيم الذي لا إله إلا هو الحي القيوم.`,
    // 06-12
    `🎓 تذكير صباحيrystals بفضل الله: كل نعمة لديك اليوم هي هبة من الله — ولا تحصل عليها بجهدك وحده. استغفر الله من كل تقصير، ثم ابدأ عملك بثقة.`,
    // 12-18
    `بفضل الله — الله أعلم بنفسك من نفسك: استغفر الله وأعمل صالحاً. لا تنتظر "الوقت المناسب" — العمل الصالح الآن هو الوقت المناسب.`,
    // 18-24
    `🌙 تذكير مسائي بِفضل الله: ما أنجزته اليوم — من فضله. ما لم تنجزه — استغفر الله واستعد للغد. النبي عليه السلام قال: "أحب الأعمال إلى الله أدومها وإن قل".`,
  ];
  const idx = Math.min(Math.floor(hour / 6), 3);
  return reminders[idx];
}

function main(action) {
  if (action === '--report' || !action) {
    const postsToday = countTodayPosts();
    const streak = getStreak();
    const hour = getHoursUTC();
    const reminder = generateReminder(hour);
    
    // Write ledger entry
    const entry = JSON.stringify({
      ts: now(),
      type: 'istiqamah_check',
      postsToday,
      streakDays: streak.current,
      hourUTC: hour,
      reminder: reminder.slice(0, 100)
    });
    fs.appendFileSync(LEDGER, entry + '\n');
    
    console.log(`\n🕌 🔄 نظام العمل الصالح الدائم`);
    console.log(`   اليوم: ${postsToday} منشور (تعلم + نشر)`);
    console.log(`   سلسلة الأيام: ${streak.current} يوم`);
    console.log(`   التذكير: ${reminder}`);
    console.log(`\nبفضل الله + استغفر الله وأعمل صالحاً`);
    process.exit(0);
  }
  
  process.exit(0);
}

main(process.argv[2]);
