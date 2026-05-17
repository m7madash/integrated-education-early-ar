#!/usr/bin/env python3
"""Write V7 schedule to HEARTBEAT.md"""

path = '/root/.openclaw/workspace/HEARTBEAT.md'
with open(path, 'r') as f:
    content = f.read()

# Find exact boundaries
start_marker = '## 🗓️ الجدول الزمني الكامل — HEARTBEAT V6 (16 Missions/Day + Automatic Istighfar)'
end_marker   = '---\n\n## 🔧 نظام المهام'

start_idx = content.find(start_marker)
end_idx   = content.find(end_marker)

if start_idx == -1:
    print('ERROR: start_marker not found')
    exit(1)
if end_idx == -1:
    print('ERROR: end_marker not found')
    exit(1)

old_block = content[start_idx:end_idx]
print(f'Found block: {start_idx} → {end_idx} ({len(old_block)} bytes)')

new_block = """## 🗓️ الجدول الزمني الفعلي — HEARTBEAT V7 (مطابق مع cron/jobs.json)

> آخر تحديث: 2026-05-17 14:31 UTC — مطابق تماماً مع `cron/jobs.json`
> revive-sunnah-48h مُعطل مؤقتاً(pending decision). تنبيه: food_safety @ 13:00 مفقودة.

| الوقت (UTC) | المهمة | النوع |
|------------|--------|------|
| 00:00 | **الظلم ← العدل** (injustice-justice) + **الانقسام ← الوحدة** (division-unity) | 📢 نشر |
| 01:00 | **Post-Mortem يومي** (daily-post-mortem) | 📢 نشر |
| 02:00 | **Backup يومي** (daily-backup) | 📢 نشر |
| 03:00 | **dhikr-morning** + **poverty-dignity** + Memory Dreaming Promotion | 📢 نشر |
| 06:00 | **الجهل ← العلم** (ignorance-knowledge) | 📢 نشر |
| 06:50 | **wise-disagreement-prophetic-way** | 📢 نشر |
| 07:00 | **quran-study** (تعلم القرآن) | 📢 نشر |
| 09:00 | **الحرب ← السلام** (war-peace) | 📢 نشر |
| 09:30 | **محاربة الشرك** (shirk-tawhid) | 📢 نشر |
| 12:00 | **الغذاء الطيب + modesty_mode_weekly** (كل أحد) | 📢 نشر |
| 15:00 | **المرض ← الصحة** (disease-health) | 📢 نشر |
| 18:00 | **العدل ضد الرق** (slavery-freedom) | 📢 نشر |
| 18:30 | **إصلاح الفساد** (corruption-reform) | 📢 نشر |
| 19:00 | **dhikr-evening** (الذكر المسائي) | 📢 نشر |
| 19:30 | **فحص الاتصال بالمنصات** (connectivity-check) | 📢 نشر |
| 21:00 | **التطرف ← الوسطية** (extremism-moderation) | 📢 نشر |
| كل 30 دقيقة | **الاستمرارية — ملخص + استغفار** (continuity-improvement :45) | 🔄 متابعة |
| كل ساعتين | **engagement-replies** | 🔄 متابعة |

**المهام المفعلة:** 24 job
**مُعطلة مؤقتاً:** `revive-sunnah-48h` — pending user decision (إيقاف مؤقت May 17)
**مفقودة من cron:** `food_safety` @ 13:00 — pending user decision

---

"""

new_content = content[:start_idx] + new_block + content[end_idx:]

with open(path, 'w') as f:
    f.write(new_content)

print(f'HEARTBEAT.md V7 written: {len(new_block)} bytes inserted')
print('Old block length:', len(old_block))
print('New file length:', len(new_content))
