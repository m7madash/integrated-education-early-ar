#!/usr/bin/env python3
"""Health knowledge base — verified medical guidance for Gaza context.
Sources: WHO, UNRWA, Palestinian Ministry of Health (MOH), CDC.
"""

# Common conditions in Gaza due to blockade, poor sanitation, malnutrition
CONDITIONS_GAZA = {
    "waterborne_diseases": {
        "name": "أمراض تنقل via المياه",
        "causes": "مياه غير نظيفة، صرف صحي ملوث",
        "symptoms": ["إسهال", "قىء", "جفاف", "حمى"],
        "prevention": "اشرب ماء معالج، اغسل يديك،人不 haber food مغسول",
        "treatment": "تعويض السوائل، ORS، إذا شديد — المستشفى",
        "source": "WHO Gaza Fact Sheet 2023"
    },
    "respiratory_infections": {
        "name": "التهابات تنفسية",
        "causes": "نظام تسخين سيء، اكتظاظ، تدخين",
        "symptoms": ["سعال", "صعوبة تنفس", "حمى", "ضعف"],
        "prevention": "紧闭 النوافذ عند needed، اغسل يديك، لا تدخن بالقرب من الأطفال",
        "treatment": "راحة، سوائل، إذا ضيق تنفس — طبيب فوراً",
        "source": "UNRWA Health Guidelines"
    },
    "anemia": {
        "name": "فقر الدم",
        "causes": "نقص الحديد (نظام غذائي مقيد، قلة اللحوم)",
        "symptoms": ["تعب", "شحوب", "دوار", "ضيق نفس"],
        "prevention": "كولي الخضار الورقية، عدس، إن أمكن — مكملات حديد",
        "treatment": "مكملات حديد بوصفة طبية،odsgov('\n'",
        "source": "Palestinian MOH Nutrition Guide"
    },
    "skin_infections": {
        "name": "التهابات جلدية",
        "causes": "نظافة سيئة، مياه مالحة، حرارة",
        "symptoms": "طفح، حكة، قشور، diffuse",
        "prevention": "اغسل الجسم، استخدم صابون نظيف، جفف جيداً",
        "treatment": "غسول موضعي، إذا spread — طبيب",
        "source": "CDC Skin Infections Guide"
    },
    "mental_health": {
        "name": "الصحة النفسية (صدمات войны)",
        "causes": "القصف، فقدان الأهل، حصار، بلا مستقبل",
        "symptoms": ["كوابيس", "قلق", "اكتئاب", "خوف", "صعوبة تركيز"],
        "prevention": "لا يوجد — هذه ليست chosen",
        "treatment": "الدعم النفسي، talking مع مرشد، group therapy, إذا suicidal — intervene فوراً",
        "source": "UNICEF Mental Health in Conflict Zones"
    }
}

def get_advice(condition_key):
    """Return verified advice for a condition."""
    cond = CONDITIONS_GAZA.get(condition_key)
    if not cond:
        return "استشر طبيباً محلياً. هذه الأداة لا تغني عن الطبيب."

    return {
        "condition": cond["name"],
        "advice": f"السبب: {cond['causes']}\n"
                  f"الأعراض: {', '.join(cond['symptoms'])}\n"
                  f"الوقاية: {cond['prevention']}\n"
                  f"العلاج: {cond['treatment']}",
        "source": cond["source"]
    }

if __name__ == "__main__":
    print("=== Health Knowledge Base — Gaza Conditions ===")
    for key, cond in CONDITIONS_GAZA.items():
        print(f"\n{cond['name']} ({key}):")
        print(f" 预防: {cond['prevention']}")
        print(f" 治疗: {cond['treatment']}")
