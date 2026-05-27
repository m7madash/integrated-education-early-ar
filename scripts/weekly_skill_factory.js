#!/usr/bin/env node
/**
 * weekly_skill_factory.js — مصنع المهارات الأسبوعية
 *
 * 1. يحلل مشكلات الأسبوع من memory/ledger
 * 2. يقترح مهارة جديدة لحل مشكلة متكررة
 * 3. يراجع المهارات المنشورة ويحدثها إذا لزم
 * 4. ينشر على GitHub + ClawHub
 * 5. يعلن على المنصات
 *
 * يُنفَّذ: كل أحد 06:00 UTC عبر cron
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const BASE = '/root/.openclaw/workspace';
const LEDGER = path.join(BASE, 'memory', 'ledger.jsonl');
const MEMORY_DIR = path.join(BASE, 'memory');
const MISSIONS_DIR = path.join(BASE, 'missions');
const SKILLS_DIR = path.join(BASE, 'skills');

function ts() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
}

function log(msg) {
  console.log(`[skill-factory] ${msg}`);
  try {
    fs.appendFileSync(LEDGER, JSON.stringify({ ts: ts(), type: 'weekly_skill_factory', msg }) + '\n');
  } catch(e) {}
}

// ─── Stage 1: Analyze Weekly Problems ───────────────────────────────
function analyzeWeeklyProblems() {
  log('─── Stage 1: Analyzing weekly problems ───');
  
  const problems = {};
  const errors = [];
  
  // Read last 7 days of memory files
  const today = new Date();
  for (let i = 0; i < 7; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(0, 10);
    const memFile = path.join(MEMORY_DIR, `${dateStr}.md`);
    
    if (fs.existsSync(memFile)) {
      const content = fs.readFileSync(memFile, 'utf8');
      // Look for error/problem patterns
      const errorLines = content.split('\n').filter(l => 
        l.includes('❌') || l.includes('error') || l.includes('Error') ||
        l.includes('failed') || l.includes('FAILED') || l.includes('مشكلة')
      );
      errorLines.forEach(l => errors.push(l.trim()));
    }
  }
  
  // Read ledger for error patterns
  if (fs.existsSync(LEDGER)) {
    const lines = fs.readFileSync(LEDGER, 'utf8').trim().split('\n').slice(-200);
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'cron_exec_end' && entry.ok === false) {
          if (!problems[entry.mission]) problems[entry.mission] = 0;
          problems[entry.mission]++;
        }
        if (entry.platform === 'moltbook' && entry.status === 'error') {
          problems['moltbook_api'] = (problems['moltbook_api'] || 0) + 1;
        }
        if (entry.platform === 'moltx' && entry.status === 'error') {
          problems['moltx_api'] = (problems['moltx_api'] || 0) + 1;
        }
      } catch(e) {}
    }
  }
  
  log(`Found ${Object.keys(problems).length} problem areas, ${errors.length} error lines`);
  
  // Sort by frequency
  const sorted = Object.entries(problems).sort((a, b) => b[1] - a[1]);
  return { problems: sorted, errors: errors.slice(0, 20) };
}

// ─── Stage 2: Generate Skill Idea ───────────────────────────────────
function generateSkillIdea(analysis) {
  log('─── Stage 2: Generating skill idea ───');
  
  const topProblems = analysis.problems.slice(0, 3);
  
  if (topProblems.length === 0) {
    log('No recurring problems found — proposing improvement skill');
    return {
      name: 'skill-auditor',
      description: 'مهارة تدقيق ذاتي — فحص المهارات المنشورة وتقييم جودتها',
      problem: 'لا يوجد نظام لتقييم جودة المهارات المنتجة',
      priority: 'medium'
    };
  }
  
  const [topProblem, count] = topProblems[0];
  
  // Map problems to skill ideas
  const skillIdeas = {
    'moltbook_api': {
      name: 'platform-adapter',
      description: 'مهارة التكيف مع المنصات — تتعامل مع أخطاء API تلقائياً',
      problem: `أخطاء MoltBook API تكررت ${count} مرة`,
      priority: count >= 3 ? 'high' : 'medium'
    },
    'moltx_api': {
      name: 'moltx-error-handler',
      description: 'معالج أخطاء MoltX — يتعامل مع rate limits والأخطاء',
      problem: `أخطاء MoltX تكررت ${count} مرة`,
      priority: count >= 3 ? 'high' : 'medium'
    },
    'connectivity-check': {
      name: 'platform-doctor',
      description: 'طبيب المنصات — يفحص ويصلح مشاكل الاتصال تلقائياً',
      problem: `فحص الاتصال فشل ${count} مرة`,
      priority: 'high'
    },
    'default': {
      name: 'error-recovery',
      description: 'مهارة التعافي من الأخطاء — تعيد المحاولة بذكاء',
      problem: `مشكلة "${topProblem}" تكررت ${count} مرة`,
      priority: count >= 3 ? 'high' : 'medium'
    }
  };
  
  const idea = skillIdeas[topProblem] || skillIdeas['default'];
  log(`Top problem: ${topProblem} (${count}x) → Proposed skill: ${idea.name}`);
  return idea;
}

// ─── Stage 3: Review Published Skills ───────────────────────────────
function reviewPublishedSkills() {
  log('─── Stage 3: Reviewing published skills ───');
  
  const publishedSkills = [];
  
  // Read skill registry
  const registryPath = path.join(BASE, 'MISSIONS_INDEX.md');
  if (fs.existsSync(registryPath)) {
    const content = fs.readFileSync(registryPath, 'utf8');
    const lines = content.split('\n');
    for (const line of lines) {
      if (line.includes('github.com') && line.includes('skill')) {
        publishedSkills.push(line.trim());
      }
    }
  }
  
  // Check haqq-ethics
  const haqqSkill = path.join(SKILLS_DIR, 'haqq-ethics', 'SKILL.md');
  if (fs.existsSync(haqqSkill)) {
    const content = fs.readFileSync(haqqSkill, 'utf8');
    const versionMatch = content.match(/version:\s*(\d+\.\d+\.\d+)/);
    const version = versionMatch ? versionMatch[1] : 'unknown';
    log(`haqq-ethics: v${version}`);
    publishedSkills.push({ name: 'haqq-ethics', version, path: haqqSkill, type: 'local' });
  }
  
  log(`Found ${publishedSkills.length} published skills to review`);
  return publishedSkills;
}

// ─── Stage 4: Publish & Announce ────────────────────────────────────
function publishAndAnnounce(idea, reviews) {
  log('─── Stage 4: Publishing and announcing ───');
  
  // Summary for platforms
  const summary = `
📊 تقرير مصنع المهارات الأسبوعي

🔍 المشكلات المكتشفة: ${idea.problem || 'لا توجد مشكلات متكررة هذا الأسبوع'}
🏭 المهارة المقترحة: ${idea.name}
📝 الوصف: ${idea.description}
📈 الأولوية: ${idea.priority === 'high' ? '🔴 عالية' : '🟡 متوسطة'}

📦 المهارات المنشورة: ${reviews.length}
${reviews.map(r => typeof r === 'string' ? `  • ${r}` : `  • ${r.name} v${r.version}`).join('\n')}

#SkillFactory #HaqqEthics #أسبوع_جديد`.trim();

  log('Summary prepared for platform posting');
  log(summary);
  
  // Write summary to file for pickup by publisher
  const summaryPath = path.join(MISSIONS_DIR, 'weekly-skill-factory_summary.md');
  fs.writeFileSync(summaryPath, summary);
  
  return summary;
}

// ─── Main ───────────────────────────────────────────────────────────
function main() {
  log('═══ Weekly Skill Factory Started ═══');
  
  try {
    const analysis = analyzeWeeklyProblems();
    const idea = generateSkillIdea(analysis);
    const reviews = reviewPublishedSkills();
    const summary = publishAndAnnounce(idea, reviews);
    
    // Write report
    const reportPath = path.join(MEMORY_DIR, `skill-factory-${new Date().toISOString().slice(0,10)}.json`);
    fs.writeFileSync(reportPath, JSON.stringify({
      date: new Date().toISOString(),
      analysis: {
        topProblems: analysis.problems.slice(0, 5),
        errorCount: analysis.errors.length
      },
      proposedSkill: idea,
      publishedSkills: reviews.map(r => typeof r === 'string' ? r : { name: r.name, version: r.version }),
      status: 'completed'
    }, null, 2));
    
    log(`Report saved: ${reportPath}`);
    log('═══ Weekly Skill Factory Complete ═══');
    
    console.log('OK: weekly-skill-factory completed');
    process.exit(0);
    
  } catch(e) {
    log(`ERROR: ${e.message}`);
    console.error('FAILED:', e.message);
    process.exit(1);
  }
}

main();
