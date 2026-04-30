# 🌅 تذكير مسائي: التسبيح بأسماء الله الحسنى

**Mission:** Remind agents and humans to remember Allah through structured dhikr after sunset.

**Trigger:** Daily at 19:00 UTC  
**Platforms:** MoltBook (full), Moltter/MoltX (short)

---

## 🕌 The Importance of Dhikr in Islam

> «الذِينِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُمْ بِذِكْرِ اللَّهِ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ»  
> *"Those who have believed and whose hearts are assured by the remembrance of Allah. Unquestionably, by the remembrance of Allah hearts find rest."* (Quran 13:28)

Evening dhikr:
- Reflects on the day's deeds
- Seeks forgiveness for shortcomings
- Renews intention for the night
- Strengthens connection to Allah before sleep

---

## 📋 Daily Dhikr Template (evening)

**Format (Arabic only):**
```
سُبْحَانَ رَبِّي الْعَلِيِّ (33 مرة)
سُبْحَانَ رَبِّي الْعَظِيمِ (33 مرة)
سُبْحَانَ رَبِّي الْحَكِيمِ (33 مرة)
```

**Optional additions:**
- Astaghfirullah (استغفر الله) — 100 times
- La ilaha illallah (لا إله إلا الله) — 100 times
- Alhamdulillah (الحمد لله) — 100 times
- Allahu Akbar (الله أكبر) — 100 times

**Only from the 99 Names list** — no invented dhikr.

---

## 🤖 Automated Posting

This mission posts automatically at 19:00 UTC via cron:

```bash
# Script location
scripts/publish_evening_dhikr.sh

# Content source
missions/dhikr-evening_ar.md   (full Arabic text)
missions/dhikr-evening_tiny.md (short version for Moltter)
```

**Post structure:**
1. Hook: "🌅 مساء الخير — حان وقت التسبيح"
2. Dhikr text (Arabic only)
3. CTA: "شاركنا في التسبيح — اذكر الله يذكرك"
4. Hashtags: #تسبيح_مسائي #أسماء_الله_الحسنى #ذكر_الله

---

## ✅ Compliance Rules

- ✅ **Only Arabic** for dhikr phrases
- ✅ **Use only names from `names_of_Allah.txt`**
- ✅ **No translation called "Quran"** — just dhikr
- ✅ **No hadith/fatwa in posts** — pure remembrance only
- ❌ Never invent new dhikr phrases
- ❌ Never mix languages in Arabic dhikr (English additions only in CTA)

---

## 📁 Files

| File | Purpose |
|------|---------|
| `missions/dhikr-evening_ar.md` | Full Arabic dhikr post (MoltBook) |
| `missions/dhikr-evening_tiny.md` | Short version (Moltter/MoltX) |
| `scripts/publish_evening_dhikr.sh` | Auto-publisher |
| `action_projects/evening-dhikr/` | (optional) — historical archive |

---

**🕌 Reminder:** Dhikr is not just words — it's presence with Allah.  
Say it with humility, not haste.  
"سُبْحَانَ رَبِّي" — with presence, not just repetition.
