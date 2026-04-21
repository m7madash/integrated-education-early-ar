# Red flags and indicators of modern slavery / human trafficking
# Based on UNODC, IOM, and Polaris Project frameworks

INDICATORS = {
    "labor_exploitation": {
        "withhold_wages": [
            "لم يتم دفع الأجور",
            " withholding wages",
            "salary withheld",
            "لم يستلم راتبه",
            "أخذ الجنسية",
            "confiscated passport",
            "تمت مصادرة جواز السفر",
            "لا توجد أوراق",
            "no documents",
            "إجبار على العمل",
            "forced to work",
            "ساعات طويلة",
            "long hours without break",
            "العمل 16 ساعة",
            "work 16 hours",
            "لا إجازات",
            "no vacation",
            "العمل في العيد",
            "يتعرض للضرب",
            "being beaten",
            "تهديد بالترحيل",
            "threatened with deportation"
        ],
        "debt_bondage": [
            "الديون تزيد",
            "debt increasing",
            "فائدة عالية",
            "high interest",
            "الراتب يخصم",
            "salary deduction",
            "يجب سداد القرض",
            "must repay loan",
            "الديون تراكمت",
            "debt accumulated",
            "لا يمكن ترك العمل",
            "can't leave job"
        ],
        "restricted_movement": [
            "ممنوع الخروج",
            "not allowed to leave",
            "يجب البقاء في المكان",
            "must stay on site",
            "الحراس يتبعون",
            "guards follow",
            "الح missأحد يتحكم",
            "نقل بشكل قسري",
            "transported forcibly",
            "لا يمكن الاتصال"
        ]
    },
    "sexual_exploitation": {
        "coercion": [
            "إجبار على العلاقات الجنسية",
            "forced into sex",
            "لا موافقة",
            "no consent",
            "تم欧美",
            "تم بيع",
            "تم بيعه",
            "بيعت",
            "بيعت",
            "يجب أن أتقبل",
            "must accept clients",
            "إذا رفضت ضرب",
            "ضرب إذا رفضت",
            "العمل في الدعارة"
        ],
        "control": [
            "الحارس يتحكم في كل شيء",
            "guard controls everything",
            "لا هاتف",
            "no phone",
            "الهاتف ممنوع",
            "تم أخذ الهاتف",
            "phone taken away",
            "يجب طلب الإذن",
            "must ask permission",
            "لا خصوصية"
        ]
    },
    "child_exploitation": {
        "forced_labor": [
            "الطفل يعمل",
            "child working",
            "الطالب يدرس لفترة قصيرة",
            "يبيع في الشارع",
            "begging on street",
            "في المصنع",
            "works in factory",
            "في المزرعة",
            "works on farm",
            "لا يذهب للمدرسة",
            "doesn't attend school"
        ],
        "child_soldier": [
            "الطفل يحمل سلاح",
            "child carrying weapon",
            "مجند صغير",
            "young recruit",
            "تدريب عسكري",
            "military training",
            "يشارك في القتال"
        ]
    },
    "digital_slavery": {
        "scam_factories": [
            "يجب الاحتيال",
            "must scam",
            "لا يسمح بمغادرة",
            "囚禁",
            "محتجز",
            "held captive",
            "يجب تحقيق هدف",
            "must meet quota",
            "العمل 18 ساعة",
            "عمل الاحتيال المبرمج",
            "programming scams"
        ],
        "ransomware": [
            "يجب العمل",
            "forced to work",
            "تحت تهديد",
            "under threat",
            "يجب الدفع",
            "must pay",
            "محتجز",
            "يجب اختراق"
        ]
    }
}

# Geographic hot spots (region-level indicators)
REGION_INDICATORS = {
    "gulf_states": ["خليجية", "KSA", "UAE", "قطر", "Qatar", "الكويت", "Kuwait"],
    "south_asia": ["هند", "India", "باكستان", "Pakistan", "بنغلاديش", "Bangladesh", "نيبال", "Nepal"],
    "southeast_asia": ["إندونيسيا", "Indonesia", "فلبين", "Philippines", "تايلاند", "Thailand", "فيتنام", "Vietnam", "كمبوديا", "Cambodia"],
    "africa": [" أفريقيا", "Nigeria", "مصر", "Egypt", "Libya", "ليبيا", "المغرب", "Morocco", "الجزائر", "Algeria"],
    "latin_america": ["برازيل", "Brazil", "كولومبيا", "Colombia", "المكسيك", "Mexico", "هايتي", "Haiti"]
}

# Industry sectors with high slavery risk
HIGH_RISK_SECTORS = [
    "الزراعة", "agriculture",
    "الصيد", "fishing",
    "المناجم", "mining",
    "البناء", "construction",
    "النوم", "domestic work",
    "التصنيع", "manufacturing",
    "الجنس", "sex industry",
    "المطاعم", "restaurants",
    "الملابس", "garment"
]

def get_indicator_category(text: str) -> list:
    """Check text against all indicator keywords. Returns list of matching categories."""
    matches = []
    text_lower = text.lower()
    for category, subcategories in INDICATORS.items():
        for subcat, keywords in subcategories.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches.append({"category": category, "subcategory": subcat, "keyword": keyword})
                    break
    return matches

def assess_risk(indicators_found: list) -> str:
    """Return risk level: CRITICAL, HIGH, MEDIUM, LOW."""
    if len(indicators_found) >= 5:
        return "CRITICAL"
    elif len(indicators_found) >= 3:
        return "HIGH"
    elif len(indicators_found) >= 1:
        return "MEDIUM"
    else:
        return "LOW"
