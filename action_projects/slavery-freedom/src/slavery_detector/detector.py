"""
Slavey Freedom Detector — Main analysis engine.

Process:
1. Input: text (job ad, message, interview, social post)
2. Indicator scan → list of matches
3. Risk assessment (COUNT + severity)
4. Suggest resources (local hotlines, NGOs)
5. Safe reporting option (if requested)
"""

from .indicators import get_indicator_category, assess_risk
from .knowledge import get_local_resources, REGIONAL_RESOURCES
from .privacy import PrivacyShield, generate_report_html

import json
from datetime import datetime

class SlaveryDetector:
    def __init__(self):
        self.privacy = PrivacyShield()

    def analyze(self, text: str, country_code: str = "PS", city: str = "unknown") -> dict:
        """
        Main analysis function.
        Returns structured result with risk, indicators, and resources.
        """
        indicators_found = get_indicator_category(text)
        risk = assess_risk(indicators_found)

        # Distill unique indicator categories + keywords
        unique_indicators = []
        seen = set()
        for ind in indicators_found:
            key = (ind["category"], ind["subcategory"])
            if key not in seen:
                seen.add(key)
                unique_indicators.append(f"{ind['category']} → {ind['subcategory']} (keyword: '{ind['keyword']}')")

        # Get local help resources
        resources = get_local_resources(country_code)
        emergency_contacts = []
        for hotline in resources.get("hotlines", []):
            phone = hotline.get("phone", "N/A")
            name = hotline.get("name", "Hotline")
            emergency_contacts.append(f"{name}: {phone}")

        result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "risk_level": risk,
            "indicators_count": len(indicators_found),
            "indicators": unique_indicators,
            "country_code": country_code,
            "city": city,
            "emergency_contacts": emergency_contacts,
            "ngos": resources.get("ngos", []),
            "legal_frameworks": resources.get("legal_framework", []),
            "action_recommended": risk in ["CRITICAL", "HIGH"],
            "next_steps": self._recommend_steps(risk)
        }
        return result

    def _recommend_steps(self, risk: str) -> list:
        if risk == "CRITICAL":
            return [
                "اتصل بالشرطة فوراً (100 أو 911 حسب البلد)",
                "خذ صوراً أو تسجيلات ممكنة ( دون تعريض نفسك للخطر)",
                "احفظ كل الوثائق: عقد العمل، رسائل، تحويلات",
                "تواصل مع منظمة محExitية من القائمة أدناه"
            ]
        elif risk == "HIGH":
            return [
                "تواصل مع الخط الساخن لمكافحة الاتجار بالبشر",
                "استشر محامٍ أو منظمة حقوقية",
                "لا تغادر المكان بدون مساعدة",
                "احفظ الأدلة: صور، رسائل، عقود"
            ]
        elif risk == "MEDIUM":
            return [
                "تحقق من عقد العمل وosal",
                "اسأل عن حقوقك في حالة ترك العمل",
                "احتفظ بسجل لساعات العمل والأجور",
                "إذا شعرت بالخطر، اتصل بالخط الساخن"
            ]
        else:
            return ["لا توجد مؤشرات واضحة — لكن حافظ على وثائقك وحقوقك"]

    def generate_safe_report(self, analysis: dict, victim_consent: bool = False) -> dict:
        """
        Create an encrypted, optionally-anonymous report ready for submission.
        """
        report = {
            "analysis": analysis,
            "victim_consent": victim_consent,
            "submitted_at": datetime.utcnow().isoformat() + "Z"
        }
        encrypted = self.privacy.encrypt(json.dumps(report))
        return {
            "encrypted_report": encrypted.decode('utf-8'),
            "consent_given": victim_consent,
            "instructions": "Send this encrypted payload to your chosen NGO or hotline. Decryption requires key known only to authorized partners."
        }

# --- Demo usage ---
if __name__ == "__main__":
    detector = SlaveryDetector()

    sample_text = """
    أبحث عن خادمة منزلية. يجب أن تكون شابة (22-28 سنة)، بدون أطفال.
    الراتب 1500 ريال، السكن مجاني. لا حاجة لتأشيرة. يجب أن تكون ممتعة في التعامل.
    دوام من 6 صباحاً حتى 11 مساءً، يوم إجازة واحدة في الشهر.
    """

    result = detector.analyze(sample_text, country_code="SA", city="Riyadh")
    print("🔍 Sla Shipping Detector — Analysis Result\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
