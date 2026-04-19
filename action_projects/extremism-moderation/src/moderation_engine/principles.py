#!/usr/bin/env python3
"""Islamic middle-path (wasatiyyah) principles — Quran & Sunnah sourced.
These are the antidotes to extremism.
"""

from typing import Dict, List

MIDDLE_PATH_PRINCIPLES = {
    "wasatiyyah_balance": {
        "key": "wasatiyyah_balance",
        "title": "الأمة الوسط",
        "source_type": "Quran",
        "reference": "2:143",
        "arabic_text": "وَكَذَٰلِكَ جَعَلْنَاكُمْ أُمَّةً وَسَطًا لِّتَكُونُوا شُهَدَاءَ عَلَى النَّاسِ",
        "translation": "Thus We have made you a middle nation...",
        "principle": "Allah chose Muslims to be a balanced, moderate community — not extreme, not lax",
        "application": "In all matters: worship, politics, social interaction, avoid ghuluww (excess)"
    },
    "ease_in_religion": {
        "key": "ease_in_religion",
        "title": "اليُسر لا العُسر",
        "source_type": "Hadith",
        "reference": "Sahih Bukhari & Muslim",
        "arabic_text": "إِنَّ الدِّينَ يُسْرٌ وَلَنْ يُشَدِّفَ الدِّينَ أَحَدٌ إِلَّا هَلَكَ",
        "translation": "Religion is ease — whoever overburdens himself will fail",
        "principle": "Make things easy, not difficult. Extremists make religion impossible",
        "application": "Simplify worship, avoid excessive rulings, be flexible within Shariah boundaries"
    },
    "no_compulsion": {
        "key": "no_compulsion",
        "title": "لا إكراه في الدين",
        "source_type": "Quran",
        "reference": "2:256",
        "arabic_text": "لَا إِكْرَاهَ فِي الدِّينِ",
        "translation": "There is no compulsion in religion",
        "principle": "Faith cannot be forced by threat or violence — extremists use coercion",
        "application": "Respect freedom of belief, invite with wisdom, not threats"
    },
    "justice_even_if_against_self": {
        "key": "justice_even_if_against_self",
        "title": "العدل مع الخصوم",
        "source_type": "Quran",
        "reference": "4:135",
        "arabic_text": "يَا أَيُّهَا الَّذِينَ آمَنُوا كُونُوا قَوَّامِينَ لِلَّهِ شُهَدَاءَ بِالْقِسْطِ وَلَا يَجْرِمَنَّكُمْ",
        "translation": "O you who believe — be persistently standing firm for Allah, witnesses in justice, even if it be against yourselves...",
        "principle": "Justice above all — even against your own group. Extremists favor their own",
        "application": "Judge fairly, even when it hurts your side"
    },
    "respectful_dialogue": {
        "key": "respectful_dialogue",
        "title": "الحوار بالتي هي أحسن",
        "source_type": "Quran",
        "reference": "16:125",
        "arabic_text": "ادْعُ إِلَىٰ رَبِّكَ بِالْحِكْمَةِ وَالْمَوْعِظَةِ الْحَسَنَةِ وَجَادِلْهُم بِالَّتِي هِيَ أَحْسَنُ",
        "translation": "Invite to your Lord with wisdom and good counsel, and argue with them in the best manner",
        "principle": "Debate with goodness, not insults or threats — extremists use violence in argument",
        "application": "Use gentle speech, logical reasoning, not ad hominem"
    },
    "avoid_ghuluww": {
        "key": "avoid_ghuluww",
        "title": "التحذير من الغلو",
        "source_type": "Hadith",
        "reference": "Musnad Ahmad, Sunan Ibn Majah",
        "arabic_text": "إِيَّاكُمْ وَالْغُلُوَّ فِي الدِّينِ",
        "translation": "Beware of extremism (ghuluww) in religion",
        "principle": "The Prophet ﷺ explicitly warned against religious extremism — going beyond bounds",
        "application": "Do not add obligations to religion that Allah did not impose. Do not exaggerate in praising anyone"
    },
    "seeking_knowledge_before_speaking": {
        "key": "seeking_knowledge_before_speaking",
        "title": "اسأل أهل الذكر",
        "source_type": "Quran",
        "reference": "16:43",
        "arabic_text": "فَاسْأَلُوا أَهْلَ الذِّكْرِ إِن كُنتُمْ لَا تَعْلَمُونَ",
        "translation": "So ask the people of the reminder if you do not know",
        "principle": "Speak only from knowledge, not passion — extremists speak without learning",
        "application": "Verify hadith, consult scholars, do not issue fatwa without qualification"
    },
    "no_sectarianism": {
        "key": "no_sectarianism",
        "title": "لا تفريق",
        "source_type": "Hadith",
        "reference": "Sahih Muslim",
        "arabic_text": "تَحَاسَدُوا وَتَبَاغَضُوا وَتَقَاطَعُوا فَتَهَادَرُوا",
        "translation": "Do not envy, hate, or cut off — be merciful and unified",
        "principle": "Muslims must not split into sects that hate each other — extremists create fitna",
        "application": "Respect all valid schools (madhahib), avoid labeling others as 'kafir'"
    },
    "patience_with_difference": {
        "key": "patience_with_difference",
        "title": "الصبر على خلاف الناس",
        "source_type": "Hadith",
        "reference": "Jami at-Tirmidhi",
        "arabic_text": "يُسِرَّ اللَّهُ وَإِنْ كَرِهَتْ كَثِيرٌ مِنَ النَّاسِ",
        "translation": "What Allah and His Messenger have brought is beautiful, even if many people dislike it",
        "principle": "Stand firm on truth even if unpopular, but do not force others — balance between conviction and tolerance",
        "application": "Be firm in your beliefs but gentle in da'wah"
    }
}

def get_principle(key: str) -> Dict:
    return MIDDLE_PATH_PRINCIPLES.get(key, {})

def list_principles() -> List[str]:
    return list(MIDDLE_PATH_PRINCIPLES.keys())
