#!/usr/bin/env python3
"""Illness → Health: Telehealth Bot for Gaza
Mission: Provide accessible, ethical, halal healthcare guidance for the oppressed.
"""

class TriageBot:
    """Classify health symptoms into urgency levels."""

    URGENT = "urgent"         # اذهب إلى المستشفى فوراً
    URGENT_SOON = "urgent_soon"  # خلال 6 ساعات
    ROUTINE = "routine"       # zieh to clinic
    SELF_CARE = "self_care"   # home care + education

    def __init__(self):
        self.conditions = self._load_conditions()

    def _load_conditions(self):
        """Common conditions in Gaza: injuries, infections, chronic diseases."""
        return {
            "heavy_bleeding": {
                "symptoms": ["نزيف غزير", "لا يتوقف النزيف", "fainting", "إغماء"],
                "urgency": self.URGENT,
                "advice": "اذهب إلى أقرب مستشفى فوراً. ضغط على النزيف بضمادة نظيفة."
            },
            "chest_pain": {
                "symptoms": ["ألم في الصدر", "ضيق تنفس", "ألم الذراع", " palpitations"],
                "urgency": self.URGENT,
                "advice": "أعراض قد تكون للقلب — اطلب الإسعاف فوراً (102)."
            },
            "severe_infection": {
                "symptoms": ["حرارة عالية", "حرارة 40", "قشعريرة", "التهاب شديد", "قىء"],
                "urgency": self.URGENT_SOON,
                "advice": "اذهب إلى عيادة طوارئ خلال 6 ساعات. قد تحتاج مضادات حيوية."
            },
            "dehydration": {
                "symptoms": ["عطش شديد", "تعب", "دوار", "تبول قليل", "جفاف"],
                "urgency": self.URGENT_SOON,
                "advice": "اشرب الماء بانتظام. إذا استمر التعب، توجه للعيادة."
            },
            "minor_wound": {
                "symptoms": ["جرح طفيف", "نزيف خفيف", "خدش", "لا غرغرينا"],
                "urgency": self.ROUTINE,
                "advice": "اغسل الجرح بالماء والصابون. ضمادة نظيفة. تغيير يومياً."
            },
            "common_cold": {
                "symptoms": ["سيلان الأنف", "sore throat", "سعال خفيف", "rhinitis", "نزلة برد"],
                "urgency": self.SELF_CARE,
                "advice": "راحة، سوائل دافئة، مسكنات خفيفة. إذا ساءت الأعراض — العيادة."
            }
        }

    def assess(self, symptoms_input):
        """Assess symptoms and return urgency + advice."""
        symptoms_input = symptoms_input.lower()
        matched = []

        for cond_id, cond in self.conditions.items():
            if any(symptom in symptoms_input for symptom in cond["symptoms"]):
                matched.append(cond)

        if not matched:
            return {
                "urgency": self.ROUTINE,
                "advice": "استشر طبيباً محلياً. لا تتجاهل الأعراض.",
                "matched_conditions": []
            }

        # Highest urgency wins
        urgency_priority = {self.URGENT: 0, self.URGENT_SOON: 1, self.ROUTINE: 2, self.SELF_CARE: 3}
        best = min(matched, key=lambda c: urgency_priority[c["urgency"]])
        return {
            "urgency": best["urgency"],
            "advice": best["advice"],
            "matched_conditions": [c for c in matched]
        }

    def urgency_ar(self, urgency):
        """Arabic urgency label."""
        labels = {
            self.URGENT: "طارئ — اذهب الآن للمستشفى",
            self.URGENT_SOON: "عاجل — خلال 6 ساعات",
            self.ROUTINE: "عادي — زيارة عيادة",
            self.SELF_CARE: "自我护理 — راحة في البيت"
        }
        return labels.get(urgency, "غير معروف")

if __name__ == "__main__":
    bot = TriageBot()
    print("=== Telehealth Bot — Gaza focus ===")
    symptoms = input("Describe your symptoms (English/Arabic): ")
    result = bot.assess(symptoms)
    print(f"\nالطلب: {bot.urgency_ar(result['urgency'])}")
    print(f"النصيحة: {result['advice']}")
    if result['matched_conditions']:
        print(f"الأسباب المحتملة: {', '.join(c for c in result['matched_conditions'])}")
