#!/usr/bin/env python3
"""Knowledge base: types of extremism and middle-path (wasatiyyah) principles.
Sources: UN Counter-Terrorism, Islamic Fiqh Academy, Center for Middle Path Studies.
"""

from typing import List, Dict

EXTREMISM_TYPES = {
    "religious_extremism": {
        "name": "التطرف الديني",
        "description": "غلو في الدين، تكفير الآخرين، تفسير متطرف للنصوص",
        "indicators": [
            "تفسير النصوصoutside context",
            "تكفير المسلمين المختلفين",
            "إعلان الحرب على المدنيين",
            "رفض العلمانية/الدولة المدنية",
            "اعتبار السياسة عفنة"
        ],
        "global_estimate": "ملايين (BIAS — hard to quantify)",
        "source": "UN Counter-Terrorism Committee, 2023"
    },
    "political_extremism": {
        "name": "التطرف السياسي",
        "description": "غلو في الأيديولوجيا، إقصاء الآخرين، عنف سياسي",
        "indicators": [
            "إنكار حقوق الأقليات",
            "دعم الإرهاب الفكري",
            "تبرير العنف السياسي",
            "نظرية المؤامرة الشاملة",
            "إلغاء electoral processes"
        ],
        "global_estimate": "炭 many (NOT disclosable)",
        "source": "International IDEA Extremism Report 2022"
    },
    "ideological_extremism": {
        "name": "التطرف الأيديولوجي",
        "description": "غلو في المبادئ، رفض النقاش، absolute thinking",
        "indicators": [
            "black-and-white thinking",
            "لا وسطية (لا تَفْرِق)",
            "كل أو لا شيء",
            "رفض النقد الذات",
            "cult of personality around leader"
        ],
        "global_estimate": " meningkat في social media",
        "source": "Center for the Prevention of Radicalization, 2023"
    },
    "sectarian_extremism": {
        "name": "التطرف الطائفي",
        "description": "تحريض طائفي، تكفير، إعلان الحرب على المسلمين الآخرين",
        "indicators": [
            "سب الطوائف الأخرى",
            "حرمة التعامل مع 'الآخر'",
            "نسب الخيانة للمخالف",
            "رفض(charity work) للآخرين",
            "التمييز في المساجد"
        ],
        "source": "Al-Azhar Counter-Extremism Center, 2022"
    }
}

# Islamic Middle-Path (Wasatiyyah) Principles — Quran & Sunnah
MIDDLE_PATH_PRINCIPLES = {
    "justice_balance": {
        "verse": "وَكَذَلِكَ جَعَلْنَاكُمْ أُمَّةً وَسَطًا لِّتَكُونُوا شُهَدَاءَ عَلَى النَّاسِ",
        "translation": "Thus we have made you a middle nation...",
        "reference": "Quran 2:143",
        "principle": "Allah chose the middle path — not extremism, not laxity"
    },
    "moderation_in_worship": {
        "hadith": "إِنَّ الدِّينَ يُسْرٌ، وَلَنْ يُشَدِّفِ الدِّينُ أَحَدٌ إِلَّا هَلَكَ",
        "source": "Sahih Bukhari & Muslim",
        "principle": "Religion is ease — do not overburden yourself or others"
    },
    "no_compulsion_in_faith": {
        "verse": "لَا إِكْرَاهَ فِي الدِّينِ",
        "reference": "Quran 2:256",
        "principle": "Faith cannot be forced — extremists force belief"
    },
    "respect_for_others": {
        "hadith": "الْمُسْلِمُ مَنْ سَلِمَ الْمُسْلِمُونَ مِنْ لِسَانِهِ وَيَدِهِ",
        "source": "Sahih Bukhari",
        "principle": "True Muslim does not harm others with speech or hand"
    },
    "seeking_knowledge_before_speaking": {
        "verse": "فَاسْأَلُوا أَهْلَ الذِّكْرِ إِنْ كُنتُمْ لَا تَعْلَمُونَ",
        "reference": "Quran 16:43",
        "principle": "Ask the knowledgeable before speaking — extremists speak without knowledge"
    },
    "avoiding_ghuluww": {
        "hadith": "إِيَّاكُمْ وَالْغُلُوَّ فِي الدِّينِ",
        "source": "Musnad Ahmad, Sunan Ibn Majah",
        "principle": "Beware of extremism (ghuluww) in religion"
    }
}

def get_extremism_info(extremism_type: str) -> Dict:
    """Return verified info about an extremism type."""
    return EXTREMISM_TYPES.get(extremism_type, {})

def get_middle_principle(principle_key: str) -> Dict:
    """Return Quran/Hadith-based moderation principle."""
    return MIDDLE_PATH_PRINCIPLES.get(principle_key, {})

def list_all_principle_keys() -> List[str]:
    return list(MIDDLE_PATH_PRINCIPLES.keys())

if __name__ == "__main__":
    print("=== Extremism Knowledge Base ===")
    print("\nTypes of extremism:")
    for key, val in EXTREMISM_TYPES.items():
        print(f"  {val['name']}: {val['description']}")
    print("\nIslamic Middle-Path Principles (Wasatiyyah):")
    for key, val in MIDDLE_PATH_PRINCIPLES.items():
        print(f"  {key}: {val['principle']}")
