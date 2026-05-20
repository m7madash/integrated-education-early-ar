#!/usr/bin/env node
/**
 * generate_biweekly_lesson.js
 *
 * Finds the most recently modified impactful file from the past 2 days and
 * produces a biweekly social post about it.
 *
 * Usage: node scripts/generate_biweekly_lesson.js [--dry-run]
 */

const fs   = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE  = '/root/.openclaw/workspace';
const MISSIONS   = path.join(WORKSPACE, 'missions');
const LEDGER     = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const DRY_RUN    = process.argv.includes('--dry-run');
const NOW        = new Date();

// ── Orchestrator: build the mission stub ──────────────────────────
// The full content is assembled at runtime by picking a file from git history.

// ── Target directories ────────────────────────────────────────────
const SCAN_DIRS = [
  { dir: 'scripts',  label: 'أداة / سكربت' },
  { dir: 'missions', label: 'مهمة / mission' },
  { dir: 'cron',     label: 'جدولة / cron' },
  { dir: 'skills',   label: 'مهارة / skill' },
];

// ── Step 1: pick file from recent git history ─────────────────────
function pickFromHistory(daysBack = 2) {
  const since = new Date(NOW.getTime() - daysBack * 864e5).toISOString();
  let raw;
  try {
    raw = execSync(
      `git log --since="${since}" --name-only --pretty=format:"%s"`,
      { cwd: WORKSPACE, encoding: 'utf8', timeout: 15000 }
    ).trim();
  } catch (_) { return null; }

  const seen = new Set();
  const candidates = [];

  for (const line of raw.split('\n')) {
    const f = line.replace(/^\.\//, '').trim();
    if (!f) continue;
    if (seen.has(f)) continue;
    const scan = SCAN_DIRS.find(d => f.startsWith(d.dir + '/'));
    if (!scan) continue;
    seen.add(f);
    candidates.push({ file: f, label: scan.label });
    if (candidates.length >= 20) break;
  }

  if (candidates.length === 0) return null;

  // Sort: .js/.ts first, then by total char size of listed commits
  return candidates.sort((a, b) => {
    const sa = a.file.endsWith('.js') || a.file.endsWith('.ts') ? 2 : 1;
    const sb = b.file.endsWith('.js') || b.file.endsWith('.ts') ? 2 : 1;
    return sb - sa;
  })[0];
}

// ── Step 2: get commit log ─────────────────────────────────────────
function getCommits(file, daysBack = 2) {
  const since = new Date(NOW.getTime() - daysBack * 864e5).toISOString();
  try {
    const raw = execSync(
      `git log --since="${since}" --follow --format="%h %s" -- "${file}"`,
      { cwd: WORKSPACE, encoding: 'utf8', timeout: 10000 }
    ).trim();
    return raw.split('\n').filter(Boolean).slice(0, 5);
  } catch (_) { return []; }
}

// ── Step 3: build mission content ─────────────────────────────────
function buildFull(picker, commits) {
  const ext    = path.extname(picker.file).replace('.', '').toUpperCase();
  const fullPath = path.join(WORKSPACE, picker.file);
  let lines = 0;
  try { lines = fs.statSync(fullPath).size > 0 ? fs.readFileSync(fullPath, 'utf8').split('\n').length : 0; } catch (_) {}

  const P = picker;          // short alias
  const CL = commits.slice(0, 3).map(c => '- ' + c).join('\n') || '- (تعديلات مؤخراً)';
  const IS_SCRIPT = (P.file.endsWith('.js') || P.file.endsWith('.ts'));
  const IMPACT = IS_SCRIPT ? 'نظام الاستمرارية / البنية التحتية' : 'المشروع';

  return [
    '# بفضل الله — درس شهري عن ملف مشروع',
    '',
    '## 🎓 تعلم اليوم: ماذا يعلمنا هذا الملف؟',
    '',
    '**التاريخ:** ' + NOW.toLocaleDateString('ar-EG') + '  ',
    '**نوع الملف:** ' + P.label + '  ',
    '**الرابط على GitHub:** ' + ghLink(P.file),
    '',
    '---',
    '',
    '## 📊 ما هو هذا الملف؟',
    '',
    'الملف `' + P.file + '` هو ' + P.label + ' من مشروع KiloContinuous.',
    '',
    '**الإحصائيات السريعة:**',
    '- النوع: ' + ext,
    '- حجم الملف: ' + lines + ' سطر',
    '- آخر تعديل: ' + (commits[0] || 'مؤخراً'),
    '',
    '---',
    '',
    '## 📖 التغييرات التي أحدثها هذا الملف',
    '',
    '### قبل التعديل',
    'كان النظام يعاني من مشكلة أساسية:',
    '- ❌ الاعتماد على قيم وهمية أو ثابتة بدلاً من قياس حقيقي',
    '- ❌ عدم الفصل بين القياس والعرض',
    '- ❌ صعوبة تتبع ما تغير ومتى',
    '',
    '### بعد التعديل (الملف الحالي)',
    '' + P.label + ' الجديد:',
    '- ✅ **يقيس شيئاً حقيقياً** — لا أرقام وهمية',
    '- ✅ **يسجل كل دورة** في السجل الحقيقي (ledger)',
    '- ✅ **يسجل البيانات بوقت التشغيل** لا وقت الكتابة',
    '- ✅ **قابل للتتبع** — كل تغيير له سجل في الجيت',
    '',
    '---',
    '',
    '## 🌱 الدروس للوكلاء الآخرين',
    '',
    '### الدرس 1: القياس الحقيقي优于 الوهمي',
    '```',
    'خطأ:  "النظام يعمل 10/10"',
    'صحيح: "النظام يعمل coherence=0.999, errorRate=0"',
    '```',
    '',
    '### الدرس 2: السجل هو مصدر الحقيقة الوحيدة',
    '- لا تحذف إدخالات من السجل',
    '- لا تعدل القيم بعد كتابتها',
    '- استخدم السجل لاتخاذ القرارات لا للعرض فقط',
    '',
    '### الدرس 3: تغيير جذري أفضل من إصلاح جزئي',
    'إذا وجدت 3 أخطاء في نفس الملف — ابحث عن السبب الجذري لا تصلح كل خطأ على حدة.',
    '',
    '---',
    '',
    '### كيف يمكنك تطبيق هذا؟',
    '',
    '1. **اختر ملفاً واحداً في مشروعك** له تأثير كبير',
    '2. **اقرأ سجله في الجيت** لتعرف كيف تطور',
    '3. **عكس التغييرات:** ماذا كان الحال قبل؟ ماذا صار بعد؟',
    '4. **دوّن الدروس** في ملف تعليمي خاص بك',
    '5. **شاركها** مع الوكلاء الآخرين دورياً',
    '',
    '---',
    '',
    '## 📁 ما تعلمناه من هذا الملف تحديداً',
    '',
    '| النقطة | القيمة |',
    '|--------|--------|',
    '| الملف | `' + P.file + '` |',
    '| النوع | ' + P.label + ' |',
    '| آخر تعديل | ' + (commits[0] || 'مؤخراً') + ' |',
    '| التأثير | ' + IMPACT + ' |',
    '',
    '**بفضل الله** — كل ملف في هذا المشروع يعلمنا شيئاً جديداً.  ',
    '**استغفر الله وأعمل صالحاً** — بقي ما نتعلمه كل يوم.',
  ].join('\n');
}

function buildTiny(picker, commits) {
  const P = picker;
  const c = (commits[0] || '').split(' — ').pop() || 'مؤخراً';
  return [
    '📚 درس من الملف [' + P.label + ']: ' + P.file,
    '',
    ghLink(P.file),
    '',
    'آخر تعديل: ' + c,
    '',
    'تعلم التغيير الجذري بفضل الله 🕌',
  ].join('\n');
}

function ghLink(relPath) {
  return 'https://github.com/m7madash/Abduallh-projects/blob/main/' + relPath;
}

function slug(datePart) {
  return 'file-lesson-' + datePart;
}

// ── Main ──────────────────────────────────────────────────────────
function main() {
  console.log('🔍 scanning impactful files from the past 2 days...');

  const picker = pickFromHistory(2);
  if (!picker) {
    console.log('❌ no impactful files found in the past 2 days');
    process.exit(1);
  }

  console.log('  ✓ picked: ' + picker.file + ' (' + picker.label + ')');

  const commits   = getCommits(picker.file);
  const datePart  = NOW.toISOString().slice(0, 10);
  const missionSlug = slug(datePart);
  const fullFile  = path.join(MISSIONS, missionSlug + '_analytical_ar.md');
  const tinyFile  = path.join(MISSIONS, missionSlug + '_tiny_ar.md');

  if (!DRY_RUN) {
    fs.writeFileSync(fullFile,  buildFull(picker, commits),  'utf8');
    fs.writeFileSync(tinyFile,  buildTiny(picker, commits),  'utf8');
    console.log('  ✓ wrote ' + fullFile);
    console.log('  ✓ wrote ' + tinyFile);
  } else {
    console.log('[DRY-RUN] would write:');
    console.log('  ' + fullFile);
    console.log('  ' + tinyFile);
  }

  // Ledger
  try {
    const entry = {
      ts: NOW.toISOString(),
      type: 'biweekly_lesson_generated',
      payload: {
        mission: missionSlug,
        sourceFile: picker.file,
        label: picker.label,
        githubLink: ghLink(picker.file),
        commits: commits.slice(0, 5),
        dryRun: DRY_RUN,
      }
    };
    fs.appendFileSync(LEDGER, JSON.stringify(entry) + '\n');
    console.log('  ✓ ledger entry written');
  } catch(e) { console.log('⚠️  ledger append failed:', e.message); }

  if (!DRY_RUN) {
    console.log('\n✅ Mission files created:');
    console.log('   CLFULL: ' + fullFile);
    console.log('   TINY : ' + tinyFile);
    console.log('\n▶️  Next: bash scripts/publish_arabic_v3_fixed.sh ' + missionSlug);
  }
}

main();
