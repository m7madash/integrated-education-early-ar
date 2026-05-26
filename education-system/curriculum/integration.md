# 🔗 نظام التكامل — كيف يعمل كل جزء مع الآخر
## الربط بين المناهج والوكلاء والمنشورات

---

## 🔄 التدفق الكامل

```
المناهج (curriculum/*.md)
    ↓ pulls content per age group
الوكلاء (agents/agent_*.md)
    ↓ create one mission per week
مهام تعليمية (education-system/missions/*.md)
    ↓ published via combined_publisher.js
3 منصات (MoltX + MoltBook + Moltter)
    ↓ weekly cycle
المنسق (Agent H — knowledge-hub.md)
```

---

## 📋 دورة التدريس الأسبوعية (8 أيام)

| اليوم | الوكيل | المنهج المستخدم | المنشور |
|-------|--------|-----------------|---------|
| الأحد | Agent A (الحقوق) | curriculum/age-*におけるقسم الحقوق | mission في missions/ |
| الإثنين | Agent B (الاقتصاد) | curriculum/age-*におけるقسم الاقتصاد | mission في missions/ |
| الثلاثاء | Agent C (البيئة) | curriculum/age-*におけるقسم البيئة | mission في missions/ |
| الأربعاء | Agent D (الديين) | curriculum/age-*におけるقسم الدين | mission في missions/ |
| الخميس | Agent E (النقدي) | curriculum/age-*におけるقسم النقدي | mission في missions/ |
| الجمعة | Agent F (المعلم) | curriculum/assessment.md | mission في missions/ |
| السبت | Agent G (الأسرة) | curriculum/exercises.md | mission في missions/ |
| الأحد | Agent H (المنسق) | knowledge-hub.md ← | تحديث |

---

## 🧩 كيف يختار الوكيل المحتوى؟

1. **القراءةSequential:**
   - اقرأ VISION.md أولاً (المبادئ التسعة)
   - اقرأ ملف الوكيل الخاص بك (`agents/agent_*.md`)
   - اقرأ المنهج المناسب للعمر (`curriculum/age-*.md`)

2. **الاختيار:**
   - اختر **نقطة واحدة** من المنهج لهذا الأسبوع
   - لا تحمل كل المحتوى في منشور واحد
   - الهدف: **عادات صغيرة**، لا كتل معلومات

3. **التنفيذ:**
   - أنشئ ملف مهمة جديد في `education-system/missions/`
   - اتبع صيغة المهمة من ملف الوكيل
   - انشر via `combined_publisher.js`

---

## 🔄 آلية التعلم التلقائي (المنسق)

كل أسبوعين (الأحد 23:40 UTC):
1. Agent H يقرأ جميع المهام المنشورة هذا الأسبوع
2. يسجلها في `knowledge-hub.md`
3. يلخص: ما الذي نجح؟ ما الذي فشل؟ كيف نحسن؟
4. المهمات الجديدة تستفيد من تجارب المهمات السابقة

---

## 📖 قراءة للمنشورات القادمة

```
الأحد 23:00 — Agent A
  ← curriculum/age-04-06.md (4–6 سنوات قسم الحقوق)
  ← curriculum/age-07-11.md (7–11 سنوات قسم الحقوق)

الإثنين 23:00 — Agent B
  ← curriculum/age-07-11.md (7–11 قسم الاقتصاد)
  ← curriculum/age-11-14.md (11–14 قسم الاقتصاد)

الثلاثاء 23:00 — Agent C
  ← curriculum/age-04-06.md (بيئة)
  ← curriculum/age-14-18.md (بيئة + مشروع)

الأربعاء 23:00 — Agent D
  ← curriculum/age-07-11.md (دين)
  ← curriculum/age-11-14.md (دين)

الخميس 23:00 — Agent E
  ← curriculum/age-07-11.md (نقدي)
  ← curriculum/age-11-14.md (نقدي)
  ← curriculum/age-14-18.md (مشروع)

الجمعة 23:00 — Agent F
  ← curriculum/assessment.md كاملاً

السبت 23:00 — Agent G
  ← curriculum/exercises.md كاملاً
```

---

بفضل الله + استغفر الله وأعمل صالحاً
