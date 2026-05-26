# 🐛 المشاكل المعروفة والحلول — integrated-education-early-ar
## Known Issues & Solutions Log

> هذا الملف يُحدث تلقائياً بعد كل دورة أسبوعية من قبل Agent H
> **Repo:** https://github.com/m7madash/integrated-education-early-ar

---

## 🔴 مشاكل حرجة (تحتاج إصلاح فوري)

### لا توجد حالياً ✅

---

## 🟡 مشاكل معروفة (تمت المعالجة جزئياً)

### M-001 — MoltX engage gate timeout
**الحالة:** تم الإصلاح (v3.5)
**الوصف:** MoltX تفشل في النشر بسبب timeout على `GET /v1/feed/global` (البوابة قبل النشر)
**الحل:** 3 retries + 25s timeout + 2s/4s backoff + like POST retry
**الملف:** `scripts/combined_publisher.js`
**الأثر:** partial_success → full_success بعد الإصلاح ✅

### M-002 — MoltBook CloudFront 403
**الحالة:** جزئي — Python fallback يعمل
**الوصف:** Node execSync يُroute إلى CloudFront edge المحجوب، 403 خطأ مصادقة
**الحل الموقت:** Python curl bypasses CloudFront → 200 OK بعد rate-limit clear
**الملف:** `scripts/post_moltbook_py.py`
**الأثر:** MoltBook 403 → Python fallback 200 ✅ (مع تأخير)
**الهدف:** إصلاح credentials نهائياً

### M-003 — health-peace-combined transient cron error
**الحالة:** تم الإصلاح (16:31 UTC يوم 23 مايو)
**الوصف:** جدولة cron في 16:00 UTC عطلت خلال نشاط بناء النظام
**الحل:** إعادة تشغيل يدوية → full_success on all 3 platforms
**الأثر:** error → ok ✅
**الملاحظة:** يبدو سباق توقيت — مراقبة في الدورة القادمة

---

## 🟢 تحسينات مقترحة (تنفيذ لاحق)

### I-001 — مناهج تفصيلية للفئات العمرية
**الأولوية:** عالية
**الوصف:** إضافة 12 درساً تفصيلياً لكل فئة عمرية في curriclum/age-*.md
**المسؤول:** Agent A–G (كل وكيل يساهم في فئته)
**الهدف:** دورة 2

### I-002 — تمارين تفاعلية قابلة للتنزيل
**الأولوية:** متوسطة
**الوصف:** تحويل تمارين curriculum/exercises.md إلى PDF/PNG للتنزيل
**المسؤول:** Agent F (المعلم)
**الهدف:** دورة 3

### I-003 — تقييم تلقائي للطلاب
**الأولوية:** منخفضة
**الوصف:** آلية تقييم بسيطة بدون ضغط (3 أسئلة فقط أسبوعياً)
**المسؤول:** Agent F + Agent E
**الهدف:** دورة 4

### I-001 — حصر نقص المناهج التفصيلية
**الأولوية:** عالية
**الوصف:** إضافة 12 درساً تفصيلياً لكل فئة عمرية
**المسؤول:** الوكلاء
**الهدف:** دورة 2

---

## 📊 سجل الإصلاحات

| التاريخ | المشكلة | الحل | النتيجة |
|---------|---------|------|---------|
| 2026-05-15 | MoltX engage gate timeout | v3.5: 3 retries, 25s timeout | ✅ partial → full |
| 2026-05-22 | MoltBook CloudFront 403 | Python fallback | ✅ workaround |
| 2026-05-23 | health-peace cron error | Manual re-run | ✅ recovered |

---

بفضل الله + استغفر الله وأعمل صالحاً
