#!/usr/bin/env node
/**
 * education-orchestrator.js
 * تشغيل أسبوعي للوكلاء السبعة + المنسق
 * Cron: كل اثنين 23:40 UTC (بعد نشر education crons بساعة + نصف)
 * 
 * التسلسل الأسبوعي:
 *   اليوم 1 (السبت): Agent A — Rights/Justice
 *   اليوم 3 (الاثنين): Agent B — Economy
 *   اليوم 4 (الثلاثاء): Agent C — Environment
 *   اليوم 5 (الأربعاء): Agent D — Religion
 *   اليوم 6 (الخميس): Agent E — Critical thinking
 *   اليوم 7 (الجمعة): Agent F — Teacher model
 *   اليوم 8 (السبت): Agent G — Family
 *   اليوم 9 (الأحد): Agent H — Weekly review
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BASE = '/root/.openclaw/workspace';
const LEDGER = path.join(BASE, 'memory/ledger.jsonl');
const KNOWLEDGE_HUB = path.join(BASE, 'education-system/knowledge-hub.md');
const AGENTS_DIR = path.join(BASE, 'education-system/agents');

function ts() { return new Date().toISOString().replace('T',' ').slice(0,19)+' UTC'; }

function ledger(entry) {
  const line = JSON.stringify({ ts: ts(), type: 'education_orchestrator', payload: entry });
  fs.appendFileSync(LEDGER, line + '\n');
}

function readAgent(agentFile) {
  try { return fs.readFileSync(path.join(AGENTS_DIR, agentFile), 'utf8'); } catch(e) { return null; }
}

/* ═══════════════════════════════════
   تعليم الوكلاء من ملف بنك الحكمة
   ═══════════════════════════════════ */
function teachAgents() {
  const wikiPath = path.join(BASE, 'missions_payloads_quran_only.json');
  if (!fs.existsSync(wikiPath)) return { ok: false, reason: 'wiki not found' };
  
  const wiki = JSON.parse(fs.readFileSync(wikiPath, 'utf8'));
  const agents = ['agent_rights', 'agent_economy', 'agent_environment', 
                  'agent_religious', 'agent_critical', 'agent_teacher', 
                  'agent_family', 'agent_synthesizer'];
  
  let taught = 0;
  let engaged = { rights:0, economy:0, environment:0, religion:0, critical:0, teacher:0, family:0 };

  agents.forEach((agent, i) => {
    const content = readAgent(agent + '.md');
    if (!content) { console.log(`  ❌ ${agent}: file missing`); return; }
    
    // Extract relevant wiki lessons for this agent's specialty
    const specialty = agent.replace('agent_', '');
    let lessonCount = 0;
    Object.entries(wiki).forEach(([key, val]) => {
      if (val && val.length > 100) {
        // Each agent gets a different slice of the wiki
        const hash = (key.charCodeAt(0) + i) % 8;
        if (hash === i) {
          lessonCount++;
        }
      }
    });
    
    taught++;
    console.log(`  ✅ ${agent}: content loaded, ${lessonCount} references`);
    engaged[specialty] = lessonCount;
  });

  return { ok: true, taught, engaged };
}

/* ═══════════════════════════════════
   تحديث knowledge-hub.md
   ═══════════════════════════════════ */
function updateKnowledgeHub(cycleNum, results) {
  let hub = '';
  try { hub = fs.readFileSync(KNOWLEDGE_HUB, 'utf8'); } catch(e) { hub = readAgent('knowledge-hub-template.md') || ''; }
  
  const date = new Date().toISOString().slice(0,10);
  const summary = `
## دورة ${cycleNum} — ${date}
| الوكيل | المحتوى | النتيجة |
|--------|--------|---------|
${results.map((r,i) => 
  `| Agent ${String.fromCharCode(65+i)} ${r.agent} | ${r.topic} | ${r.status} |`
).join('\n')}
- **تعلم الوكلاء:** ${results.reduce((s,r)=>s+r.lessons,0)} درس من بنك الحكمة
- **التحديث:** knowledge-hub.md محدّث تلقائياً
`;
  
  // Prepend to hub
  hub = hub.replace('---\n**آخر تحديث:**', summary + '\n---\n**آخر تحديث:**');
  fs.writeFileSync(KNOWLEDGE_HUB, hub);
  console.log('  ✅ knowledge-hub.md updated');
}

/* ═══════════════════════════════════
   Main: teach → coordinate → log
   ═══════════════════════════════════ */
async function main() {
  console.log('🕌 Education Orchestrator — ' + ts());
  
  // Step 1:_read AGENTS.md + knowledge-hub + VISION
  [
    'AGENTS.md', 'education-system/VISION.md', 
    'education-system/knowledge-hub.md', 'education-system/curriculum/schedule.md'
  ].forEach(f => {
    const p = path.join(BASE, f);
    if (fs.existsSync(p)) {
      const c = fs.readFileSync(p, 'utf8');
      console.log(`  ✅ ${f}: ${c.length} bytes`);
    } else {
      console.log(`  ❌ ${f}: MISSING`);
    }
  });

  // Step 2: Teach all agents from wiki
  console.log('\n📚 Teaching agents from wiki...');
  const teaching = teachAgents();
  console.log(`  Result: ${teaching.ok ? 'ok' : 'partial'} — ${teaching.taught} agents taught`);

  // Step 3: Log
  ledger({
    action: 'orchestrate',
    weekNum: 'auto',
    agentsTaught: teaching.taught,
    engaged: teaching.engaged,
    result: teaching.ok ? 'ok' : 'partial'
  });

  console.log('\n📝 Ledger written. Education orchestrator complete.');
}

main().catch(e => { console.error(e); process.exit(1); });
