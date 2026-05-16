#!/usr/bin/env node
/**
 * Revive Sunnah Engine — Evolutionary Curriculum
 *
 * Cycles through sunnah topics in progressive difficulty:
 * Level 1 (basic) → Level 2 (intermediate) → Level 3 (advanced)
 * Each cycle reviews previous + introduces new sunnah.
 * Output: Markdown mission file for publishing.
 *
 * Integration: Called by cron (every 48 hours) or manually.
 */

const fs = require('fs');
const path = require('path');

const ROOT = '/root/.openclaw/workspace';
const CURRICULUM_FILE = path.join(ROOT, 'data', 'sunnah_curriculum.json');
const PROGRESS_FILE = path.join(ROOT, 'memory', 'sunnah_progress.json');
const MISSIONS_DIR = path.join(ROOT, 'missions');
const LOG_FILE = path.join(ROOT, 'memory', 'revive_sunnah_log.jsonl');

function log(entry) {
  fs.appendFileSync(LOG_FILE, JSON.stringify({ ts: new Date().toISOString(), ...entry }) + '\n');
}

function loadCurriculum() {
  return JSON.parse(fs.readFileSync(CURRICULUM_FILE, 'utf8'));
}

function loadProgress() {
  if (!fs.existsSync(PROGRESS_FILE)) {
    const initial = {
      current_cycle: 1,
      current_level: 'level1_basic',
      current_sunnah_index: 0,
      completed_sunnahs: [],
      mastered_levels: [],
      start_date: new Date().toISOString().slice(0,10),
      history: []
    };
    fs.writeFileSync(PROGRESS_FILE, JSON.stringify(initial, null, 2));
    return initial;
  }
  return JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf8'));
}

function saveProgress(p) {
  fs.writeFileSync(PROGRESS_FILE, JSON.stringify(p, null, 2));
}

/**
 * Get next sunnah to teach based on progress
 * Rules:
 * 1. If current level has more sunnahs → next index
 * 2. If level completed → move to next level, reset index
 * 3. If all levels done → cycle back to level1 (review cycle)
 */
function getNextSunnah() {
  const curr = loadProgress();
  const allLevels = ['level1_basic', 'level2_intermediate', 'level3_advanced'];
  const levelKey = curr.current_level;
  const level = curriculum.curriculum[levelKey];
  const idx = curr.current_sunnah_index;

  // Check if current level exhausted
  if (idx >= level.sunnahs.length) {
    // Mark level as mastered
    if (!curr.mastered_levels.includes(levelKey)) {
      curr.mastered_levels.push(levelKey);
    }
    // Move to next level (or cycle)
    const nextLevelIdx = allLevels.indexOf(levelKey) + 1;
    if (nextLevelIdx < allLevels.length) {
      curr.current_level = allLevels[nextLevelIdx];
      curr.current_sunnah_index = 0;
      curr.current_cycle = Math.ceil((curr.current_cycle || 0) + 0.5); // half-cycle
    } else {
      // All levels done → Cycle back to level1 (full review cycle)
      curr.current_level = 'level1_basic';
      curr.current_sunnah_index = 0;
      curr.current_cycle = (curr.current_cycle || 0) + 1;
    }
  }

  const nextSunnah = curriculum.curriculum[curr.current_level].sunnahs[curr.current_sunnah_index];
  return { sunnah: nextSunnah, progress: curr };
}

/**
 * Generate mission markdown
 */
function generateMission(sunnah, cycle, levelName, isReview) {
  const title = `إحياء السنن (الدورة ${cycle}): ${sunnah.title}`;
  const content = `# 🕌 ${title}

## 📌 المستوى: ${levelName}

> **"وَاتَّبِعُوا سُنَّةَ مَنْ أَنْزَلَ اللَّهُ عَلَيْهِ كِتَابَهُ»** [الأعراف:157]

---

## 📖 النص القرآني مرتبط:
${sunnah.quran_ref ? `**${sunnah.quran_ref}** — {renal} — تذكّر بأهمية اتباع السنة` : '—'}

---

## 🎤 السنة النبوية (البيان):
> **"${sunnah.hadith_text}"**
> — ${sunnah.hadith_ref}

---

## 🔍 الواقع المعاصر (ما حدثنا):
${sunnah.reality}

---

## ✅ كيف نطبق (خطوات عملية):

${sunnah.application.split('\n').map(step => `- ${step}`).join('\n')}

---

## 🗓  برنامج التطبيق (هذا الأسبوع):

| اليوم | العمل |
|-------|-------|
| اليوم 1–2 | قراءة الحديث وفهمه |
| اليوم 3–4 | مراقبة نفسك: هل تفعله؟ |
| اليوم 5–7 | تطبيقه عملياً (حتى لو قليلاً) |

---

## 🕌 الربط الشرعي:

- **القرآن:** يامر بأداء العبادة/الفعل
- **السنة:** تبين **كيفية** الأداء
- **إجماع الصحابة:** تطبيق عملي مؤكد

---

## 💬 سؤال للنقاش:
ما التحدي الذي واجهتك في تطبيق هذه السنة؟ كيف تتغلب عليه؟

#إحياء_السنن #سنة_نبوية #متابعة_السنن
`;

  return { title, content };
}

// --- Main ---
const curriculum = loadCurriculum();
const next = getNextSunnah();
const sunnah = next.sunnah;
const prog = next.progress;

// Generate mission file
const cycleNum = prog.current_cycle;
const levelName = curriculum.curriculum[prog.current_level].name;
const missionBase = `revive_sunnah_cycle${cycleNum}_${sunnah.id}`;
const missionPath = path.join(MISSIONS_DIR, `${missionBase}.md`);

const { title, content } = generateMission(sunnah, cycleNum, levelName, false);
fs.writeFileSync(missionPath, content, 'utf8');

// Update progress
prog.current_sunnah_index++;
prog.completed_sunnahs.push({
  id: sunnah.id,
  title: sunnah.title,
  completed_at: new Date().toISOString(),
  cycle: cycleNum,
  level: prog.current_level
});
saveProgress(prog);

// Log
log({
  action: 'sunnah_mission_created',
  mission: missionBase,
  sunnah_id: sunnah.id,
  cycle: cycleNum,
  level: prog.current_level,
  next_index: prog.current_sunnah_index
});

console.log(`✅ Generated: ${missionBase}.md`);
console.log(`   Level: ${prog.current_level} (${prog.current_sunnah_index}/${curriculum.curriculum[prog.current_level].sunnahs.length})`);
console.log(`   Cycle: ${cycleNum}`);
console.log(`   Completed sunnahs total: ${prog.completed_sunnahs.length}`);

process.exit(0);
