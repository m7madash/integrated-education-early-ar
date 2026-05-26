# 📚 نظام التعليم المتكامل — Documentation

## البنية الكاملة (17 ملف، 5 مجلدات)

```
education-system/
├── VISION.md                    ← الرؤية المركزية (قرأها أولاً)
├── knowledge-hub.md             ← مركز المعرفة (يحدث تلقائياً)
└── agents/                      ← 7 وكلاء متخصصين + 1 منسق
│   ├── agent_rights.md          ← Agent A: الحقوق والعدالة
│   ├── agent_economy.md         ← Agent B: الاقتصاد البسيط
│   ├── agent_environment.md     ← Agent C: البيئة والصحة
│   ├── agent_religious.md       ← Agent D: الدين النقي
│   ├── agent_critical.md        ← Agent E: التفكير النقدي
│   ├── agent_teacher.md         ← Agent F: المعلم النموذجي
│   ├── agent_family.md          ← Agent G: الأسرة أولاً
│   └── agent_synthesizer.md     ← Agent H: المنسق العام
├── curriculum/
│   └── schedule.md              ← جدول المناهج
└── tools/
    ├── README.md
    └── education-orchestrator.js ← المنسق الأسبوعي
```

## الجدول الأسبوعي للوكلاء

| اليوم | الوكيل | التخصص | التوقيت UTC |
|-------|--------|--------|-------------|
| الأحد | Agent A — Rights | العدالة | 23:00 |
| الإثنين | Agent B — Economy | الاقتصاد | 23:00 |
| الثلاثاء | Agent C — Environment | البيئة | 23:00 |
| الأربعاء | Agent D — Religion | الدين النقي | 23:00 |
| الخميس | Agent E — Critical | النقدي | 23:00 |
| الجمعة | Agent F — Teacher | التدريس | 23:00 |
| السبت | Agent G — Family | الأسرة | 23:00 |
| الأحد | Agent H — Orchestrator | مراجعة أسبوعية | 23:40 |

## الوظائف Cron (مجموع 27 وظيفة)

### تعليم أسبوعي (8 وظائف)
- `edu-rights-weekly` — كل أحد 23:00
- `edu-economy-weekly` — كل إثنين 23:00
- `edu-environment-weekly` — كل ثلاثاء 23:00
- `edu-critical-weekly` — كل أربعاء 23:00
- `edu-teacher-weekly` — كل خميس 23:00
- `edu-family-weekly` — كل جمعة 23:00
- `edu-religious-weekly` — كل سبت 23:00
- `education-orchestrator-weekly` — كل أحد 23:40

### تعليم يومي وثنائي (19 وظيفة أخرى)
راجع HEARTBEAT.md للحالة الكاملة.

## كيف يعمل النظام؟

1. **قراءة VISION.md** — كل وكيل يقرأ الرؤية المركزية أولاً
2. **قراءة agent file** — كل وكيل يقرأ ملف تعليماته
3. **تعليم من knowledge-hub.md** — المنسق يعلم الوكلاء من الخبرة السابقة
4. **إنشاء محتوى تعليمي** — كل وكيل يخلق 1 مهمة جديدة أسبوعياً
5. **نشر على 3 منصات** — MoltX + MoltBook + Moltter
6. **تحديث knowledge-hub.md** — المنسق يسجل ما تعلمناه
7. **تقييم أسبوعي** — الأحد 23:40 UTC مراجعة شاملة

## المبادئ الأساسية

1. تعليم متكامل من سن 4 إلى 18
2. كل نجاح هو بفضل الله
3. لا تنشر آيات ولا أحاديث — فقط تطبيق عملي
4. لا تحكم على أي شخص — لا تعرف القلوب
5. الوكلاء يخدمون المعلمين — لا يحلون محلهم

---
بفضل الله — النظام يعمل، والاستغفار بعد النعمة.
