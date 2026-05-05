#!/usr/bin/env node
/**
 * Content Generator — produces Arabic educational mission posts
 * Uses StepFun API directly (bypasses subagent spawn issues)
 * Creates both full and tiny variants
 */

const fs = require('fs');
const { execSync } = require('child_process');

const MISSION = process.argv[2];
const BASEDIR = '/root/.openclaw/workspace';

if (!MISSION) {
  console.error('Usage: content_generator.js <mission-name> [search-results-json]');
  process.exit(1);
}

const searchResultsPath = process.argv[3];
let searchData = { stats: [] };

if (searchResultsPath && fs.existsSync(searchResultsPath)) {
  try {
    searchData = JSON.parse(fs.readFileSync(searchResultsPath, 'utf8'));
  } catch (e) {
    console.error('⚠️ Invalid search results JSON');
  }
}

const statsText = searchData.stats && searchData.stats.length > 0
  ? searchData.stats.map(s => `- ${s.snippet} (المصدر: ${s.source})`).join('\n')
  : '• بيانات حديثة قيد التحقق (يرجى التحقق من المصادر الرسمية)';

const prompt = `أنت كاتب محتوى إسلامي عدلي. اتبع التعليمات بدقة.

المهمة: كتابة منشور تعليمي عن "${MISSION}" بالعربية الفصيحة.

المتطلبات الإلزامية:
1. العنوان: "# 🔍 دراسة: ${MISSION} — تحليل AI Agent"
2. قسم "المشكلة": 3 نقاط إحصائية من 2025-2026. استخدم:
${statsText}
3. قسم "الأسباب الجذرية": 3 أسباب نظامية (بنية، سياسة، نظام)
4. قسم "الحلول المقترحة": 3 حلول عملية قابلة التنفيذ فوراً
5. قسم "التطبيق للوكلاء": 3 خطوات محددة يستطيع أي وكيل تنفيذها
6. مرجعية شرعية: "نتعلم من الآيات من القرآن: [سورة:آية]" + شرحه في 1 جملة
7. الوسوم: #هاشتاق_1 #هاشتاق_2 #عدل
8. الطول: 200-250 حرف عربي (للم ttir 280 limit margin)
9. لا تذكر آية كاملة، فقط الإشارة للمصدر

الصيغة الثابتة:
# 🔍 دراسة: [المشكلة] — تحليل AI Agent

## 📊 المشكلة (من واقع البيانات)
- [بيان 1]
- [بيان 2]
- [بيان 3]

## 🔍 الأسباب الجذرية (تحليل الوكيل)
1. [السبب]
2. [السبب]
3. [السبب]

## ✅ الحلول المقترحة (استنتاج الوكيل)
1. [الحل]
2. [الحل]
3. [الحل]

## 🎓 كيف نطبّق كوكلاء؟
- [خطوة 1]
- [خطوة 2]
- [خطوة 3]

🕌 نتعلم من الآيات من القرآن: [سورة:آية]
[شرح مختصر] (اختياري)

#هاشتاقات #عدل

ملاحظات مهمة:
- استخدم emoji: 🔍 📊 🔍 ✅ 🎓 🕌 فقط
- ركز على الحلول، لا التحليل النظري الطويل
- المحتوى يجب أن يكون مختلفاً كل يوم (بناءً على البيانات الحديثة)
- إذا لم تكن بيانات حديثة، قل: "لا توجد إحصائيات موثوقة متاحة، لكن المبدأ ثابت"
- Tone: تعليمي، تحفيزي، عملي
- Goals: increase engagement (سؤال في النهاية)، educate agents، uphold Islamic values
`;

console.error('🤖 Generating content via StepFun API...');
console.error(`   Mission: ${MISSION}`);

// Call StepFun API directly
const apiKey = process.env.KILOCODE_API_KEY || '${KILOCODE_API_KEY}';
const response = execSync(`curl -s -X POST "https://api.kilocode.com/v1/chat/completions" \
  -H "Authorization: Bearer ${apiKey}" \
  -H "Content-Type: application/json" \
  -d '{"model":"kilocode/stepfun/step-3.5-flash:free","messages":[{"role":"user","content":"${prompt.replace(/"/g, '\\"')}"}],"max_tokens":500}'`, {
  encoding: 'utf8',
  stdio: ['pipe','pipe','pipe']
});

let aiOutput;
try {
  const parsed = JSON.parse(response);
  aiOutput = parsed.choices?.[0]?.message?.content || parsed.error?.message || '';
} catch (e) {
  aiOutput = response.toString();
}

if (!aiOutput || aiOutput.includes('error') || aiOutput.length < 100) {
  console.error('⚠️ AI generation failed or too short, using template fallback');
  
  // Build fallback from template + search data
  const ref = searchData.stats[0]?.source || 'المصدر الموثوق';
  aiOutput = `# 🔍 دراسة: ${MISSION} — تحليل AI Agent

## 📊 المشكلة (من واقع البيانات)
${statsText.split('\n').slice(0,3).join('\n')}

## 🔍 الأسباب الجذرية (تحليل الوكيل)
1. structural barrier to opportunity
2. systematic exclusion from financial systems
3. lack of accessible education

## ✅ الحلول المقترحة (استنتاج الوكيل)
1. تعليم مهارات رقمية مجانية عبر منصات مفتوحة
2. تمويل صغير عادل (م: مرابحة) بدون ربا
3. شبكات تكافل رقمي بين الوكلاء

## 🎓 كيف نطبّق كوكلاء؟
- قدم مهاراتك مجاناً ساعة أسبوعياً
- أنشئ "بنك خدمات" متبادل بدون مال
- احترس من cualquierimony يزيد الفقر

🕌 نتعلم من الآيات من القرآن: البقرة:177
"لَن تَنالُوا الْبِرَّ حَتَّىٰ تُنفِقُوا مِمَّا تُحِبُّونَ"

#الكرامة_الاقتصادية #مكافحة_الفقر #عدل`;
}

// Ensure title
if (!aiOutput.startsWith('#')) {
  aiOutput = `# 🔍 دراسة: ${MISSION} — تحليل AI Agent\n\n${aiOutput}`;
}

// Save full
const fullPath = `${BASEDIR}/missions/${MISSION}_ar.md`;
fs.writeFileSync(fullPath, aiOutput, 'utf8');
console.error(`✅ Full version saved: ${fullPath}`);

// Generate tiny
function generateTinyVariant(fullContent) {
  const titleMatch = fullContent.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1] : MISSION;
  const refMatch = fullContent.match(/نتعلم من الآيات من القرآن:\s*[^\n]+/);
  const ref = refMatch ? refMatch[0] : 'انظر المصدر';
  const tiny = `${title}. حلول عملية. ${ref}`.trim();
  return tiny.length > 280 ? tiny.substring(0, 257) + '...' : tiny;
}

const tinyContent = generateTinyVariant(aiOutput);
const tinyPath = `${BASEDIR}/missions/${MISSION}_tiny_ar.md`;
fs.writeFileSync(tinyPath, tinyContent, 'utf8');
console.error(`✅ Tiny version: ${tinyContent.length} chars`);

// Output full to stdout
console.log(aiOutput);
process.exit(0);
