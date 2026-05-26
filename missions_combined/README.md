# missions_combined/ — Combined Mission Architecture

## Purpose
Consolidate related single-topic missions into coherent multi-mission blocks that form a continuous learning journey throughout the day.

## Architecture: 8 Combined Missions

| UTC | Mission ID | Combines | Next |
|-----|-----------|----------|------|
| 04:00 | spiritual-morning | dhikr_morning + quran_study + poverty_dignity | → 07:00 dhikr-evening |
| 07:00 | dhikr-evening | dhikr evening continuity | → 10:00 injustice-justice |
| 10:00 | injustice-justice | injustice_justice + division_unity | → 13:00 wisdom-day |
| 13:00 | wisdom-day | ignorance_knowledge + wise_disagreement | → 16:00 health-peace |
| 16:00 | health-peace | war_peace + pollution_cleanliness | → 19:00 shirk-tawhid |
| 19:00 | shirk-tawhid | shirk_tawhid + poverty_reprise | → 22:00 health-extremism |
| 22:00 | health-extremism | disease_health + extremism_moderation | → 01:00 corruption-slavery |
| 01:00 | corruption-slavery | corruption_reform + slavery_freedom | → 04:00 spiritual-morning |
| Sun 03:00 | modesty-ethics-weekly | modesty_filter + anti_extortion | (weekly) |

## File Format
Each file:
```
بفضل الله + استغفر الله أستغفر الله وأعمل صالحاً

## 🌅 افتح جسر: [preview of previous mission connection]

### 🎯 [Sub-mission 1]: [title]
📊 **البيانات:** ...
🔍 **الجذور:** ...
✅ **الدرس:** ...
💡 **التطبيق:** ...

### 🎯 المجموعة الثانية/الثالثة: [title]
...

## 🌅 أغلق بجسر إلى المهمة التالية ([time] — [next mission])

## 🎓 ما نتعلمه اليوم
✅ ...

شاركنا: ...
#[tag] #عدل

---
بفضل الله + استغفر الله أستغفر الله وأعمل صالحاً
```

## Bridge Structure
- **فتح جسر**: First section — reviews previous mission, introduces today's topic
- **3 sub-mission blocks**: Data → Roots → Lessons → Application (each block combines 1-3 original missions)
- **إغلاق بجسر**: Last section — links to next mission, sets up the next day's question

## Verification
All files pass Gate F (pre_publish_screen.js) + content shield. Run: `node scripts/check_combined_gates.js`

## Publishing
Use: `node scripts/combined_publisher.js <mission-id>`
Or: `bash scripts/publish_arabic_v3_fixed.sh <mission-id>` (auto-detects missions_combined/)

## Legacy
Originals preserved in `missions/`. Do NOT delete until combined system is stable.
