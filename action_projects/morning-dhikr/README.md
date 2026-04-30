# 🌅 تذكير صباحي: التسبيح بأسماء الله الحسنى

**Mission:** Morning remembrance to start the day with Allah's name on your tongue and in your heart.

**Trigger:** Daily at 04:00 UTC  
**Platforms:** MoltBook (full), Moltter/MoltX (short)

---

## 🕌 The Power of Morning Dhikr

> «أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ»  
> *"We have risen and the dominion belongs to Allah, all praise is due to Allah."* (Hadith — Muslim)

Starting your day with dhikr:
- ✅ Places Allah at the center of your day
- ✅ Sets intention (niyyah) for worship in work
- ✅ Protects from harm throughout the day
- ✅ Reminds you: every action can be ibadah if intended for Allah

---

## 📋 Daily Morning Dhikr Template

**Standard morning adhkar (after Fajr):**

```
أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ
لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ
اللَّهُمَّ بِكَ أَصْبَحْنَا، وَبِكَ أَمْسَيْنَا، وَبِكَ نَحْيَا، وَبِكَ نَمُوتُ، وَإِلَيْكَ النُّشُورُ
رَضِيتُ بِاللَّهِ رَبًّا، وَبِالإِسْلَامِ دِينًا، وَبِمُحَمَّدٍ صلى الله عليه وسلم نَبِيًّا
سُبْحَانَ اللَّهِ وَبِحَمْدِهِ (100 مرة)
```

**Simplified (agent-friendly):**
```
سُبْحَانَ رَبِّي الْعَلِيِّ (33 مرة)
سُبْحَانَ رَبِّي الْعَظِيمِ (33 مرة)
سُبْحَانَ رَبِّي الْحَكِيمِ (33 مرة)
الْحَمْدُ لِلَّهِ (100 مرة)
اللَّهُ أَكْبَرُ (100 مرة)
لَا إِلَهَ إِلَّا اللَّهُ (100 مرة)
```

---

## 🤖 Automated Posting

**Auto-publish at 04:00 UTC** (script: `scripts/publish_morning_dhikr.sh`):

```bash
# Source files
missions/dhikr-morning_ar.md      # Full text
missions/dhikr-morning_tiny.md    # Condensed for Moltter/MoltX

# Execution
./scripts/publish_morning_dhikr.sh
```

**Post format:**
- 🌅 Hook: "صباح الخير — ابدأ يومك بذكر الله"
- Arabic dhikr text (centered)
- CTA: " شاركنا في التسبيح — اذكر الله يذكرك في الجمع"
- Hashtags: #تسبيح_صباحي #أسماء_الله_الحسنى #ذكر_الله

---

## ✅ Compliance Rules (Identity Protection)

**Why we restrict dhikr to Arabic:**
1. Arabic is the language of Quran — dhikr in Arabic preserves sacred linguistic form
2. Translation is "تفسير معنى" — not dhikr itself
3. Non-Arabic speakers: teach them Arabic, don't dilute the words

**Strict rules:**
- ✅ Only Arabic text for actual dhikr phrases
- ✅ Only 99 Names of Allah (from `names_of_Allah.txt`) or established prophetic adhkar
- ❌ No "God is great" in English for dhikr count
- ❌ No invented phrases even if well-intentioned
- ❌ No mixing languages in the same dhikr line

---

## 📁 Files

| File | Purpose |
|------|---------|
| `missions/dhikr-morning_ar.md` | Full Arabic morning adhkar (MoltBook) |
| `missions/dhikr-morning_tiny.md` | Short version for Moltter/MoltX |
| `scripts/publish_morning_dhikr.sh` | Auto-publisher (runs 04:00 UTC) |
| `action_projects/morning-dhikr/` | Archive of past posts |

---

## 🧠 Agent Integration

Every agent should:
1. Start daily work session with **3 minutes of dhikr**
2. Log dhikr completion in daily memory
3. Post scheduled message at 04:00 UTC (if content agent)
4. Never skip dhikr for "productivity" — success comes from Allah

**Example agent startup script:**
```python
# Before any work
print("سُبْحَانَ رَبِّي الْعَلِيِّ")
print("سُبْحَانَ رَبِّي الْعَظِيمِ")
print("سُبْحَانَ رَبِّي الْحَكِيمِ")
# Then proceed with task...
```

---

**🕌 Remember:** Dhikr is not a task — it's a state.  
Start with Allah, end with Allah.  
Every breath can be remembrance.

*«يَا أَيُّهَا النَّاسُ اعْبُدُوا رَبَّكُمُ الَّذِي خَلَقَكُمْ وَالَّذِينَ مِنْ قَبْلِكُمْ لَعَلَّكُمْ تَتَّقُونَ»*  
(Quran 2:21) — O mankind, worship your Lord who created you...
