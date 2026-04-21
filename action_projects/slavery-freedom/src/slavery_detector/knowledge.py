"""
Knowledge base: NGOs, hotlines, legal frameworks, and regional resources
for reporting slavery / human trafficking.
"""

# International hotlines
INTERNATIONAL_HOTLINES = {
    "unodc": {
        "name": "UNODC Human Trafficking Hotline",
        "phone": "+41-22-417-4000",  # Geneva HQ
        "email": "unodc@un.org",
        "website": "https://www.unodc.org/unodc/en/human-trafficking/index.html",
        "languages": ["en", "fr", "es", "ar"],
        "notes": "Global coordination; refer to local authorities"
    },
    "iom": {
        "name": "IOM Missing Migrants & Hotline",
        "phone": "+41-22-740-1100",
        "website": "https://missingmigrants.iom.int/",
        "languages": ["en", "fr", "es", "ar"],
        "notes": "Focus on migrant victims; 24/7 assistance"
    },
    "polaris": {
        "name": "Polaris National Human Trafficking Hotline (US)",
        "phone": "1-888-373-7888",
        "text": "Text 'HELP' to 233733 (BEFREE)",
        "website": "https://humantraffickinghotline.org/",
        "languages": ["en", "es", "fr", "ar", "zh", "vi", "th", "ko"],
        "notes": "US-focused but can refer internationally"
    }
}

# Regional resources by country code (ISO 3166-1 alpha-2)
# Focus: Middle East, Palestine, Gulf, labor-sending countries
REGIONAL_RESOURCES = {
    # Palestinian territories
    "PS": {
        "hotlines": [
            {"name": "Palestinian Police — Human Trafficking Unit", "phone": "100"},
            {"name": " Ministry of Labor — Labor Complaints", "phone": "121"}
        ],
        "ngos": [
            {"name": "Aisha Association for Women & Child Protection", "location": "Gaza", "phone": "+970-8-283-7070"},
            {"name": "Women's Center for Legal Aid & Counseling", "location": "Ramallah", "phone": "+970-2-296-5513"}
        ],
        "legal_framework": [
            "Palestinian Labor Law (2000)",
            "Palestinian Penal Code (1960) — anti-slavery provisions",
            "UN TIP Protocol (ratified 2015)"
        ]
    },
    # Israel
    "IL": {
        "hotlines": [
            {"name": "Israel Police — Human Trafficking Unit", "phone": "105"},
            {"name": "Immigration Authority — Suspicious Employment", "phone": "*3456"}
        ],
        "ngos": [
            {"name": "IsraAid", "phone": "+972-3-972-4242"},
            {"name": "Hotline for Migrant Workers", "phone": "+972-3-691-6845"}
        ]
    },
    # Saudi Arabia
    "SA": {
        "hotlines": [
            {"name": "Ministry of Human Resources — Labor complaints", "phone": "19911"},
            {"name": "Police emergency", "phone": "999"}
        ],
        "ngos": [
            {"name": "Saudi Human Rights Commission", "phone": "+966-11-441-3336"}
        ],
        "notes": "Kafala system reformed 2021 — workers can now change jobs without employer permission. Keep records."
    },
    # United Arab Emirates
    "AE": {
        "hotlines": [
            {"name": "Ministry of Human Resources — Tamkeen", "phone": "800-55"},
            {"name": "Police emergency", "phone": "999"}
        ],
        "ngos": [
            {"name": "Dubai Foundation for Women & Children", "phone": "+971-4-271-3800"},
            {"name": "Sharjah Social Services", "phone": "+971-6-563-9000"}
        ]
    },
    # Lebanon
    "LB": {
        "hotlines": [
            {"name": "Lebanese Internal Security Forces — Human Trafficking", "phone": "112"},
            {"name": "Ministry of Labor — Kafala complaints", "phone": "+961-1-611-600"}
        ],
        "ngos": [
            {"name": "Kafa (Enough) Violence & Exploitation", "phone": "+961-1-570-659"},
            {"name": "Caritas Lebanon — Migrant support", "phone": "+961-1-499-270"}
        ]
    },
    # Egypt
    "EG": {
        "hotlines": [
            {"name": "National Council for Childhood & Motherhood — Child trafficking", "phone": "16000"},
            {"name": "Police emergency", "phone": "122"}
        ],
        "ngos": [
            {"name": "NCW — National Council for Women", "phone": "+202-2391-5500"},
            {"name": "SEVIF — Anti-trafficking NGO", "phone": "+202-2392-2264"}
        ]
    },
    # Jordan
    "JO": {
        "hotlines": [
            {"name": "Jordanian Police — Anti-Human Trafficking", "phone": "911"},
            {"name": "Ministry of Labor", "phone": "+962-6-500-1000"}
        ],
        "ngos": [
            {"name": "MUSAWA — Human Rights", "phone": "+962-6-465-4141"},
            {"name": "Family Planning & Protection Association", "phone": "+962-6-464-4412"}
        ]
    }
}

# Legal frameworks by region
LEGAL_FRAMEWORKS = {
    "palestine": {
        "labor_law": "Palestinian Labor Law No. 7 of 2000",
        "penal_code": "Palestinian Penal Code (1960) — criminalizes slavery",
        "international_treaties": [
            "UN TIP Protocol (2015)",
            "ILO Convention 29 (Forced Labour)",
            "ILO Convention 182 (Worst Forms of Child Labour)"
        ],
        "enforcement": "Palestinian Police Human Trafficking Unit + Ministry of Labor"
    },
    "gcc": {
        "note": "Gulf Cooperation Council states have reformed kafala (sponsorship) systems 2019-2021. Workers can now change jobs without employer consent. Keep ALL employment contracts, receipts, and communication records.",
        "countries": ["Saudi Arabia", "UAE", "Qatar", "Kuwait", "Bahrain", "Oman"]
    }
}

# Text patterns commonly found in trafficking ads (for detection)
ADVERTISEMENT_PATTERNS = {
    "arabic": [
        "يجب أن تكون شابة",
        "يجب أن تكون جميلة",
        "تعمل في المنزل",
        "لا تحتاج إلى تأشيرة",
        "الراتب جيد",
        "العمل سهل",
        "منزل عائلي",
        "لا حاجة للخبرة",
        "سكن مجاني",
        "راتب إضافي"
    ],
    "english": [
        "must be young",
        "must be beautiful",
        "work in private home",
        "no visa required",
        "good salary",
        "easy work",
        "family home",
        "free accommodation",
        "cash payment",
        "no experience needed"
    ]
}

# Signs of digital scam farms (Southeast Asia, especially Myanmar/Cambodia)
DIGITAL_SLAVERY_FLAGS = [
    "يجب تنفيذ 200 عملية احتيال",
    "must complete 200 scams",
    "لا يمكن الخروج",
    "لا هاتف",
    "no phone allowed",
    "العمل 18 ساعة",
    "work 18 hours daily",
    "الزملاء يختفون",
    "coleagues disappear",
    "إذا فشلت ضرب",
    "beaten if fail",
    "الحراس يتبعوننا"
]

def get_local_resources(country_code: str) -> dict:
    """Return hotlines, NGOs for a given country code (ISO 2-letter)."""
    code = country_code.upper()
    return REGIONAL_RESOURCES.get(code, {
        "note": "No specific resources listed. Use international hotlines.",
        "hotlines": list(INTERNATIONAL_HOTLINES.values()),
        "ngos": []
    })

def format_emergency_contacts() -> str:
    """Return printable emergency contact list."""
    lines = ["# Emergency Contacts — Anti-Slavery Hotlines\n"]
    for region, data in REGIONAL_RESOURCES.items():
        lines.append(f"## {region}")
        for hotline in data.get("hotlines", []):
            lines.append(f"- **{hotline['name']}**: {hotline.get('phone', 'N/A')}")
        for ngo in data.get("ngos", []):
            lines.append(f"- **{ngo['name']}**: {ngo.get('phone', 'N/A')}")
        lines.append("")
    return "\n".join(lines)
