# Case Studies — Slavery → Freedom Detector

## Case 1: Domestic Worker Exploitation (Saudi Arabia)
**Text:** "أبحث عن خادمة منزلية. يجب أن تكون شابة (22-28 سنة)، بدون أطفال. الراتب 1500 ريال، السكن مجاني. لا حاجة لتأشيرة. يجب أن تكون ممتعة في التعامل. دوام من 6 صباحاً حتى 11 مساءً، يوم إجازة واحدة في الشهر."

**Indicators detected:**
- `labor_exploitation → withhold_wages` (withhold_wages, long hours, no vacation)
- `labor_exploitation → restricted_movement` (no visa, employer retains control)
- `sexual_exploitation` (sexualized requirement "must be pleasant")

**Risk level:** HIGH

**Next steps:** Contact Saudi Labor hotline (19911), keep all messages, document work conditions.

---

## Case 2: Fishing Industry Forced Labor (Indonesia)
**Text:** "العمال يعملون 18 ساعة يومياً. الأجور لا تدفع أبداً. جوازات السفر محفوظة عند Captain. لا يسمح بالاتصال بالعائلة. debt يتراكم."

**Indicators detected:**
- `labor_exploitation → withhold_wages` (wages not paid)
- `labor_exploitation → debt_bondage` (debt accumulation, passport confiscation)
- `labor_exploitation → restricted_movement` (cannot contact family, 18h shifts)

**Risk level:** CRITICAL

**Next steps:** Immediate contact with IOM (+41-22-740-1100), preserve evidence, seek consular assistance.

---

## Case 3: Digital Scam Farm (Myanmar/Cambodia)
**Text:** "يجب تنفيذ 200 عملية احتيال يومياً. إذا فشلت، ضرب. لا هاتف مسموح. لا يمكن الخروج من المبنى. Coleague اختفى بعد فشله."

**Indicators detected:**
- `digital_slavery → scam_factories` (200 scams/day quota, beatings, no phone, colleagues disappear)

**Risk level:** CRITICAL

**Next steps:** Contact anti-trafficking hotline immediately, document building layout, collect names of guards if possible.

---

## Case 4: Normal Job Ad (Control)
**Text:** "نبحث عن مسؤول تسويق. خبرة سنتين في مجال التسويق الرقمي. راتب تنافسي + عمولات. أوفيس في دبي. أي nationalities مسموح."

**Indicators detected:** none

**Risk level:** LOW

**Next steps:** No action. Document for baseline.

---

## Case 5: Child Labor (Egypt)
**Text:** "صبي عمره 12 سنة يعمل في ورشة تصليح سيارات. لا يذهب للمدرسة. يعمل من الفجر حتى المساء. الراتب 500 جنيه فقط."

**Indicators detected:**
- `child_exploitation → forced_labor` (child working, no school, long hours)

**Risk level:** HIGH

**Next steps:** Contact Egypt child protection hotline (16000), provide location details.
