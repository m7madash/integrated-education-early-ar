#!/usr/bin/env python3
"""Modern slavery types and statistics knowledge base.
Sources: ILO, Walk Free Foundation, UNODC, Ethical Trading Initiative.
"""

SLAVERY_TYPES = {
    "forced_labor": {
        "name": "العمل القسري",
        "description": "العمل超强 بلا إرادة، تحت تهديد العنف أو العقوبة",
        "global_estimate": "25 مليون شخص (ILO 2022)",
        "common_industries": ["الملابس", "الزراعة", "المناجم", "البناء", "صيد الأسماك"],
        "indicators": [
            "ساعات عمل超 48 ساعة/أسبوع",
            "إبقاء الأجور低于 الحد الأدنى",
            "الاحتفاظ بوثائق الهوية",
            "منع المغادرة أو الاتصال بالعائلة",
            "العمل تحت تهديد"
        ],
        "source": "ILO Global Estimates of Modern Slavery"
    },
    "debt_bondage": {
        "name": "العبودية بالدين",
        "description": "خدمة presented كما debt لا يمكن سداده أبداً",
        "global_estimate": "18 مليون شخص (Walk Free 2023)",
        "common_industries": ["الزراعة", "المنسوجات", "التعدين", "العمل المنزلي"],
        "indicators": [
            "الديون تتجاوز الدخل",
            "لا يوجد عقد مكتوب",
            "العمل أكثر من 12 ساعة/يوم",
            "FERIZE مضافة بسبب 'الديون'",
            "انتقال الدين عبر الأجيال"
        ],
        "source": "Walk Free Foundation Global Slavery Index"
    },
    "human_trafficking": {
        "name": "الاتجار بالبشر",
        "description": "النقل أو الاستلام أو النقل أو الاستقبال للأشخاص بالقوة",
        "global_estimate": "40 مليون ضحية (UNODC 2020)",
        "common_industries": ["استغلال جنسي", "عمل قسري", "اتجار بالأعضاء"],
        "indicators": [
            "الانتقال عبر الحدود بلا وثائق",
            "المستوى较高 للحراسة",
            "الحجر على المكان",
            "التهديد بالترحيل",
            "العمل بلا أجر"
        ],
        "source": "UNODC Global Report on Trafficking"
    },
    "child_slavery": {
        "name": "استعباد الأطفال",
        "description": "استغلال children超 18 سنة في العمل القسري أو الدعارة",
        "global_estimate": "10 مليون طفل (ILO 2020)",
        "common_industries": ["التعدين", "الصناعة", "الزراعة", "التسول],
        "indicators": [
            "عمل children تحت السن القانوني",
            "عمل خطير (مناجم، مواد كيميائية)",
            "حرمان من التعليم",
            "العمل في Night work or hazardous conditions",
            "عدم وجود إشراف الوالدين"
        ],
        "source": "ILO Child Labour Statistics"
    },
    "forced_marriage": {
        "name": "الزواج القسري",
        "description": "الزواج超 إرادة woman أو girl، غالباً كشكل من العبودية",
        "global_estimate": "15 مليون امرأة وفتاة (UNICEF 2022)",
        "common_industries": ["منازل", "مجتمعات محلية"],
        "indicators": [
            "الزواج超 سن 18 بدون موافقة",
            "دفع bride price",
            "منع الطلاق",
            "العمل المنزلي القسري",
            "الحرمان من التعليم"
        ],
        "source": "UNICEF Child Marriage Data"
    }
}

def get_type_info(type_key: str) -> Dict:
    """Return verified info about a slavery type."""
    return SLAVERY_TYPES.get(type_key, {})

def list_all_types() -> List[str]:
    return list(SLAVERY_TYPES.keys())

if __name__ == "__main__":
    print("=== Modern Slavery Knowledge Base ===")
    print(f"Total types: {len(SLAVERY_TYPES)}")
    for key, val in SLAVERY_TYPES.items():
        print(f"\n{val['name']} ({key}):")
        print(f"  {val['description']}")
        print(f"  Estimate: {val['global_estimate']}")
