#!/usr/bin/env python3
"""Unity actions — concrete steps to bridge divisions."""

from typing import List

def get_unity_actions(division_type: str) -> List[str]:
    """Return actionable steps to heal a specific division."""
    actions = {
        "sectarian": [
            "نظيم حوارات بين الطوائف Different faith leaders meet",
            "إنشاء مشاريع مشتركة (تعليم، صحة) تربط الناس",
            "تبادل الزيارات بين مجتمعات مختلفة",
            "إطلاق حملة 'نحن جميعاً بشر' على社交媒体",
            "إقامة إفطار/إفطار مشترك في رمضان"
        ],
        "political": [
            "Finding common ground on local issues",
            "Create cross-party working groups on shared interests",
            "Host debates with respectful rules of engagement",
            "Focus on local problems, not national ideology",
            " Build coalitions around single-issue campaigns"
        ],
        "regional": [
            "تحديد موارد مطلوبة مشتركة (ماء، كهرباء)",
            "إنشاء لجان فنية مشتركة للحل",
            "تبادل الخبرات (منطقة غزة ↔ الضفة ↔ القدس)",
            "توحيد الجهد في المحافل الدولية",
            "تنسيق الإغاثة عبر الحدود"
        ]
    }
    return actions.get(division_type, [
        "حدد طبيعة الانقسام (مذهبي؟ سياسي؟ جغرافي؟)",
        "اجمع الأطراف المتنافسة في ورشة عمل",
        "حدد هدفاً مشتركاً يمكن الجميع التحمس له",
        "أنشئ آلية اتخاذ قرار مشتركة",
        "احتفل بالنجاحات الصغيرة معاً"
    ])

if __name__ == "__main__":
    print("=== Unity Actions for Different Divisions ===\n")
    for dtype in ["sectarian", "political", "regional"]:
        print(f"{dtype.upper()}:")
        for action in get_unity_actions(dtype)[:3]:
            print(f"  • {action}")
        print()
