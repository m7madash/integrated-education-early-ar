/**
 * 🔄 Education Pipeline — من المشكلة إلى المنشور التعليمي
 * 
 * التحويل: بيانات المشكلة ← تحليل ← منهج ← منشور تعليمي ← نشر
 * 
 * الاستخدام:
 *   node pipeline.js <problem-file.json>
 * 
 * المدخل (problem-file.json):
 *   { "domain": "rights|economy|environment|religious|critical|teacher|family",
 *     "data": "نص المشكلة والبيانات",
 *     "source": "المصدر",
 *     "ageTarget": "04-06|07-11|11-14|14-18" }
 */

const fs = require('fs');
const path = require('path');

const AGENTS_DIR = path.join(__dirname, '..');
const CURRICULUM_DIR = path.join(educationSystemDir(), 'curriculum');
const MISSIONS_DIR = path.join(workspaceRoot(), 'missions');
const EDU_MISSIONS_DIR = path.join(educationSystemDir(), 'missions');

function educationSystemDir() { return path.join(__dirname, '..'); }
function workspaceRoot() { return path.join(__dirname, '..', '..'); }

// خريطة الوكلاء حسب المجال
const AGENTS = {
  rights: 'agent_rights.md',
  economy: 'agent_economy.md',
  environment: 'agent_environment.md',
  religious: 'agent_religious.md',
  critical: 'agent_critical.md',
  teacher: 'agent_teacher.md',
  family: 'agent_family.md'
};

// خريطة المناهج حسب العمر
const CURRICULUM_MAP = {
  '04-06': 'age-04-06.md',
  '07-11': 'age-07-11.md',
  '11-14': 'age-11-14.md',
  '14-18': 'age-14-18.md'
};

/**
 * Step 1: قراءة بيانات المشكلة
 */
function loadProblem(problemFile) {
  const raw = fs.readFileSync(problemFile, 'utf8');
  return JSON.parse(raw);
}

/**
 * Step 2: تحليل المشكلة (يستخدم المنطق المناسب للمجال)
 */
function analyze(problem) {
  const domain = problem.domain || 'teacher';
  const analysis = {
    domain,
    title: problem.title || 'مشكلة تعليمية',
    ageTarget: problem.ageTarget || '07-11',
    facts: extractFacts(problem.data),
    rootCause: identifyRootCause(problem.data, domain),
    lesson: generateLesson(problem.data, domain),
    exercise: generateExercise(problem.data, domain, problem.ageTarget || '07-11'),
    curiosity: generateCuriosityQuestion(problem.data, domain)
  };
  return analysis;
}

function extractFacts(data) {
  const sentences = data.split(/[.؟!\n]/).filter(s => s.trim().length > 10);
  return sentences.slice(0, 3).map(s => s.trim());
}

function identifyRootCause(data, domain) {
  const causes = {
    rights: 'غياب الوعي بالحقوق + ضعف الحماية',
    economy: 'نظام مالي غير عادل + غياب الوعي المالي',
    environment: 'سلوكيات استهلاكية + غياب الوعي البيئي',
    religious: 'غياب الفهم الصحيح + التقليد الأعمى',
    critical: 'انتشار المعلومات + غياب مهارات التحقق',
    teacher: 'أساليب تقليدية + غياب التعلم النشط',
    family: 'غياب الحوار + ضعف الوعي التربوي'
  };
  return causes[domain] || 'أسباب متعددة متشابكة';
}

function generateLesson(data, domain) {
  const lessons = {
    rights: [
      'كل إنسان له حقوق — بغض النظر عن عمره أو بلده',
      'الظلم لا يدوم — لكن الصمت عنه يطيله',
      'التغيير يبدأ بشخص واحد يقول "هذا  unfair"'
    ],
    economy: [
      'المال أداة — ليس غاية',
      'العدالة الاقتصادية تبدأ من الوعي',
      'كل قرار مالي يومي يؤثر في المجتمع'
    ],
    environment: [
      'الأرض أمانة — لا نملكها بل نستعيرها',
      'التلوث لا يحده حدود — الهواء مشترك',
      'التغيير البيئي يبدأ بسلوك واحد'
    ],
    religious: [
      'الفهم أهم من الحفظ',
      'التحقق من المصدر واجب — ليس خيار',
      'الدين علاقة مع الله — ليس قواعد جامدة'
    ],
    critical: [
      'ليس كل ما يُقال صحيح — حتى لو كرره الآلاف',
      'السؤال "كيف عرفت؟" أقوى من أي إجابة',
      'التحقق ليس ضعف — هو قوة'
    ],
    teacher: [
      'المعلم الحقيقي يسأل — لا يجيب',
      'الطفل الذي يسأل "لماذا؟" يتعلم أكثر 10 مرات',
      'الخطأ فرصة تعليمية — لا عقوبة'
    ],
    family: [
      'البيت أول مدرسة — قبل أي كتاب',
      '5 دقائق حوار = ساعة درس',
      'القدوة أقوى من 1000 كلمة'
    ]
  };
  return lessons[domain] || lessons.teacher;
}

function generateExercise(data, domain, ageTarget) {
  const exercises = {
    '04-06': 'ارسم صورة عن المشكلة — وأرها لشخص كبير. اسأله: "ماذا تفعل لو كنت مكان هذا الشخص؟"',
    '07-11': 'اكتب 3 أسئلة عن المشكلة. ابحث عن إجابة واحدة فقط. شاركها مع صديق.',
    '11-14': 'حلل المشكلة في 5 جمل: ماذا حصل؟ لماذا؟ من المتأثر؟ ما الحل؟ ما دورك؟',
    '14-18': 'ابحث عن بيانات إحصائية عن المشكلة. تحقق من المصدر. اكتب تقرير من 200 كلمة.'
  };
  return exercises[ageTarget] || exercises['07-11'];
}

function generateCuriosityQuestion(data, domain) {
  const questions = {
    rights: 'لو كنت مكان الشخص المظلوم — ماذا كنت تتمنى أن يفعل الناس؟',
    economy: 'هل تعتقد أن المال يجلب السعادة؟ — ماذا عن شخص غني لكنه غير سعيد؟',
    environment: 'بعد 100 سنة — ماذا سيجد الناس لو استمررنا هكذا؟',
    religious: 'ما الفرق بين شخص يصلي خوفًا وشخص يصلي حبًا؟',
    critical: 'كم خبر سمعته اليوم — وكم تحققت منه؟',
    teacher: 'ما أفضل سؤال سألك معلمك — ولماذا بذكرك؟',
    family: 'ما الشيء الوحيد الذي تعلمته من أهلك ولا تتعلمه في المدرسة؟'
  };
  return questions[domain] || questions.teacher;
}

/**
 * Step 3: ربط بالمنهج
 */
function linkCurriculum(analysis) {
  const map = {
    '04-06': { stage: 'المرحلة 1 — البذرة والنمو', focus: 'العادات البسيطة والأسئلة' },
    '07-11': { stage: 'المرحلة 2 — الاكتشاف والتطبيق', focus: 'المهارات العملية والتحليل البسيط' },
    '11-14': { stage: 'المرحلة 3 — التحليل والتفكير', focus: 'التفكير النقدي وربط الأسباب' },
    '14-18': { stage: 'المرحلة 4 — المشروع والتأثير', focus: 'المشاريع الحقيقية والتقييم' }
  };
  return map[analysis.ageTarget] || map['07-11'];
}

/**
 * Step 4: إنتاج المنشور التعليمي
 */
function producePost(problem, analysis, curriculum) {
  const now = new Date();
  const domainLabels = {
    rights: 'حقوق وعدالة',
    economy: 'اقتصاد',
    environment: 'بيئة وصحة',
    religious: 'تربية دينية',
    critical: 'تفكير نقدي',
    teacher: 'تعليم وتعلم',
    family: 'أسرة'
  };

  const post = `# 🎓 ${analysis.title}

## 📅 التاريخ: ${now.toISOString().slice(0,10)}
## 🎯 التعلم من الواقع: ${domainLabels[analysis.domain] || 'تعليم متكامل'}

---

## 🎓 تعلم اليوم
**${analysis.curiosity}**

هذه ليست مشكلة بعيدة — هذه حياتنا.
والمسألة ليست فقط "ما الذي حصل" بل "**ماذا نتعلم منها؟**"

---

## ✅ ما نتعلمه

### الدرس الأول: ${analysis.lesson[0]}
عندما نفهم أن كل مشكلة لها سبب جذري — نتوقف عن لوم الضحايا ونبدأ بالبحث عن الحل.

### الدرس الثاني: ${analysis.lesson[1]}
الوعي هو الخطوة الأولى. من لا يفهم المشكلة لا يستطيع حلها.

### الدرس الثالث: ${analysis.lesson[2]}
التغيير يبدأ بفرد واحد. قد تكون أنت ذلك الفرد.

---

## 💡 كيف نطبق اليوم؟

### تمرين عملي:
${analysis.exercise}

**المدة**: ${analysis.ageTarget === '04-06' ? '10 دقائق' : analysis.ageTarget === '07-11' ? '20 دقيقة' : '30 دقيقة'}
**المستوى**: ${curriculum.stage} — ${curriculum.focus}

---

## 🌱 تعليم الوكلاء
- لا تكرر المشكلة — حوّلها لدرس
- كل خبر سلبي فيه بذرة تعلم إيجابي
- الطالب لا يحتاج أن يعرف كل الأخبار السيئة — بل يحتاج أن يفهم كيف يفكر
- اسأل أكثر مما تُجيب
- كل محتوى تعليمي يُبنى على: الواقع ← التحليل ← الدرس ← التطبيق

---

## 🕌 الخلاصة

بفضل الله + استغفر الله وأعمل صالحاً

---

📅 **تاريخ النشر**: ${now.toISOString().slice(0,10)}
🎯 **النوع**: تعليم من الواقع — ${curriculum.stage}
🔖 **المصدر**: ${problem.source || 'بيانات مفتوحة'}
`;

  return post;
}

/**
 * Step 5: كتابة المنشور للملف
 */
function savePost(post, problem, analysis) {
  const slug = problem.slug || analysis.title.replace(/[^a-zA-Z0-9\u0600-\u06FF]/g, '-').replace(/-+/g, '-').toLowerCase();
  const now = new Date();
  const datePrefix = now.toISOString().slice(0, 10);
  const filename = `curriculum-${analysis.domain}-${slug}_education.md`;
  const filepath = path.join(MISSIONS_DIR, filename);
  fs.writeFileSync(filepath, post, 'utf8');
  return { filename, filepath };
}

/**
 * Pipeline الرئيسي
 */
function runPipeline(problemFile) {
  console.log('🔄 Education Pipeline — من المشكلة إلى المنشور التعليمي\n');

  // Step 1
  console.log('📥 Step 1: قراءة المشكلة...');
  const problem = loadProblem(problemFile);
  console.log(`  المجال: ${problem.domain} | العمر: ${problem.ageTarget || '07-11'}`);

  // Step 2
  console.log('🧠 Step 2: التحليل...');
  const analysis = analyze(problem);
  console.log(`  السبب الجذري: ${analysis.rootCause}`);

  // Step 3
  console.log('📚 Step 3: ربط بالمنهج...');
  const curriculum = linkCurriculum(analysis);
  console.log(`  المنهج: ${curriculum.stage}`);

  // Step 4
  console.log('✍️ Step 4: إنتاج المنشور...');
  const post = producePost(problem, analysis, curriculum);

  // Step 5
  console.log('💾 Step 5: حفظ المنشور...');
  const saved = savePost(post, problem, analysis);
  console.log(`  المحفوظ: ${saved.filename}`);

  console.log(`\n✅ المنشور التعليمي جاهز للنشر!`);
  console.log(`📄 ${saved.filepath}`);
  console.log(`🚀 للنشر: cd ${workspaceRoot()} && node scripts/combined_publisher.js ${saved.filename.replace('_education.md', '').replace('.md', '')}`);

  return { problem, analysis, curriculum, post, saved };
}

// CLI
const problemFile = process.argv[2];
if (!problemFile) {
  console.log('الاستخدام: node pipeline.js <problem-file.json>');
  console.log('مثال: node pipeline.js problems/pollution-01.json');
  process.exit(1);
}

try {
  runPipeline(problemFile);
} catch (err) {
  console.error('❌ خطأ:', err.message);
  process.exit(1);
}
