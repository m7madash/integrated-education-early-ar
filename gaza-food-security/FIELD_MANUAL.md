# manual field manual — دليل الميدان
# مشروع غزة الغذائي

## **📱 بطاقة الاستخدام السريع**

```
خطوة 1: التسجيل
 $ ./1_assessment/register_family.sh FAM001 6 3 1 1500 0599123456
 ❶ العائلة: FAM001 (6 أفراد، 3 أطفال، 1 مسن)
 ❷ الدخل: 1500 شيكل
 ❸ النتيجة: score 14 → CRITICAL (توزيع أسبوعي)

خطوة 2: إصدار بطاقة
 $ ./2_smart_distribution/card_system.sh generate FAM001 14
 ❶ البطاقة: GF-20260502-ABC123
 ❷ الرصيد: 820 شيكل/شهر
 ❸ المسموح: أرز، عدس، زيت، حليب، سكر

خطوة 3: التوزيع
 $ ./2_smart_distribution/card_system.sh deduct GF-20260502-ABC123 rice 5 3.5
 ❶ المشتري: 5 كغ أرز × 3.5 شيكل = 17.5 شيكل
 ❷ الرصيد المتبقي: 802.5 شيكل

خطوة 4: المراقبة
 $ python3 5_monitoring/early_warning.py
 ❶ يتحقق من المخزون في 5 مراكز
 ❷ يرسل تنبيهات إذا < 100 كغ
```

---

## **🎯 سيناريوهات الاستخدام**

### **السيناريو 1: أسرة جديدة تظهر (مع مدخلات كاملة)**

```bash
# عامل اجتماعي يسجل أسرة
./1_assessment/register_family.sh \
  FAM12345 \
  8    # members
  5    # children
  2    # elderly
  1800 # income NIS/month
  0599888777 # phone

# Output:
# ✅ Family FAM12345 registered with priority score: 18
# 🎯 Category: CRITICAL — distribute weekly

# System automatically:
# 1. Adds to families_register.json
# 2. Calculates monthly allocation: 1050 NIS
# 3. Flags for immediate card generation
```

**النتيجة:** الأسرة في النظام، جاهزة لاستلام البطاقة خلال 24 ساعة.

---

### **السيناريو 2: center يطلب إعادة تموين**

```bash
# مركز الزيتون يريد إعادة المخزون
# اليدوي: center manager يملأ طلب

cat > reorder_request.json <<EOF
{
  "center_id": "gaza_01_zeitoun",
  "requested_by": "أبو سالم",
  "items": [
    {"item": "rice_kg", "qty": 1000},
    {"item": "lentils_kg", "qty": 500},
    {"item": "oil_liters", "qty": 300}
  ],
  "urgency": "high"
}
EOF

# النظام يتحقق تلقائياً:
# -库存 الحالي: rice = 1800kg (threshold 1000kg) → OK
# - lentils = 800kg (threshold 1000kg) → WARNING
# - oil = 400kg (threshold 500kg) → WARNING

# إذا كان < threshold → generate auto-PO
```

**النتيجة:** طلب إعادة تموين يرسال للموردين المحليين.

---

### **السيناريو 3: تحدث أزمة (حصار مفاجئ)**

```bash
# System automatically:
# 1. Early warning detects stock dropping fast
# 2. Increases distribution frequency for all families
# 3. Activates emergency protocol: every family gets 10kg emergency ration

# Manual override (if needed):
./2_smart_distribution/card_system.sh emergency_enable ALL
# All cards: balance × 2 for 30 days

# Notify all families via SMS:
./5_monitoring/alert_families.sh "emergency" "إعلان طوارئ: سيتم توزيع حصص إضافية خلال 24 ساعة"
```

---

### **السيناريو 4: متطوع يريدTraining"

```bash
# Registration for training
cd 3_local_production
./register_trainee.sh "أحمد محمد" 25 0599123456
# Adds to waiting list
# Automatic scheduling: 3-day course, next batch starts 2026-05-10

# Before training:
cat training_curriculum.md > printed_handout.pdf
```

---

## **📊 التقارير اليومية (automated)**

### **Report 1: الشفافية اليومية** (00:00 UTC)
```bash
./5_monitoring/transparency_report.sh
# Creates: reports/daily/2026-05-02_report.md
# Publishes to: 
#   - website (public)
#   - telegram channel @gaza_food_transparency
#   - email to donors
```

**Content:**
```
# تقرير يومي — 2026-05-02

## 📊 الأرقام
- الأسر المسجلة: 1,234
- البطاقات المصدرة: 987
- قيمة التوزيع: 45,670 شيكل
- المخزون المتبقي: 12.5 طن

## 💰 المالية
- التبرعات: 12,500 شيكل
- المصروفات: 9,800 شيكل
- الرصيد: 2,700 شيكل

## 🚨 التنبيهات
- مركز الزيتون: الأرز منخفض (900kg) — طلب إعادة
- مركز خانيونس: OK

## 📞 للتواصل
0599123456
```

---

### **Report 2: early warning check** (كل 6 ساعات)
```bash
python3 5_monitoring/early_warning.py
# Outputs to: alerts.log
# If critical: sends SMS to admin + creates ticket
```

---

## **🔧 الصيانة (weekly)**

| المهمة |时长 | المسؤول |
|--------|------|---------|
| reconciliation of ledger | 2h | المبرمج |
| backup database | 30min | مسؤول النظام |
| check card expiry | 1h | موظف |
| center inventory audit | 3h/center | مراقب |
| update donor list | 1h | المالية |

---

## **🆘 طوارئ (common)**

### **مشكلة: البطاقة لا تعمل في center**
```bash
# Check card status
./2_smart_distribution/card_system.sh status GF-20260502-ABC123
# If blocked: unblock
./2_smart_distribution/card_system.sh unblock GF-20260502-ABC123
```

### **مشكلة: center منخفض على thing سريع**
```bash
# Manual override (if system didn't auto-order)
./5_monitoring/manual_reorder.sh gaza_01_zeitoun rice 2000
# Creates PO and notifies supplier
```

### **مشكلة: family تسجل مرتين (احتيال)**
```bash
# Query by phone
grep "0599123456" 1_assessment/families_register.json
# If duplicate: merge records, flag for review
```

---

## **📱 استفاده من الهاتف**

يمكن المشغلين استخدام الهاتف عبر:

```bash
# SMS registration (manual)
echo "REGISTER FAM67890 4 2 0 1200 0599666777" | send_sms_gateway.sh

# Query card balance
echo "BALANCE GF-20260502-ABC123" | send_sms_gateway.sh

# Alert center (low stock)
echo "ALERT gaza_01_zeitoun rice 450kg" | send_sms_gateway.sh
```

---

## **🕌 الضوابط الشرعية في التشغيل**

### **يومياً:**
- [ ] التأكد من عدم وجود تحايل (لا أسر مسجلة مرتين)
- [ ] مراجعة المصاريف: كلها múi đích
- [ ] تقرير الشفافية ينشر في الوقت المحدد

### **أسبوعياً:**
- [ ] تدقيق مالي (أي اختلاس → إيقاف فوري)
- [ ] مراجعة الأولويات (هل العائلات المُحاة هي الأكثر حاجة؟)
- [ ] تحديث قائمة الموردين (إضافة/حذف)

### **شهرياً:**
- [ ] تقييم الأثر: كم أسرة خرجت من الجوع؟
- [ ] مراجعة الشفافية مع المجتمع (اجتماع عام)
- [ ] تخطيط الشهر القادم (budget + capacity)

---

## **📞 خطوط الاتصال (urgent)**

| الحالة | الإجراء | الرقم |
|--------|---------|-------|
| البطاقة لا تعمل | فني البطاقات | 0599123456 |
| center لا يوجد فيه thing | مدير التوزيع | 0598123456 |
| مشكلة في النظام (tech) | الدعم التقني | 0597123456 |
| شكوى من مستفيد | مدير المشروع | 0599123457 |
| طوارئ أمنية | الإدارة العليا | 0599123458 |

---

## **✅ قائمة الـ Go-Live (قبل التشغيل الكامل)**

- [ ] 10,000 أسرة مسجلة (test batch)
- [ ] 5,000 بطاقة مُصدرة
- [ ] 5 مراكز توزيع fully stocked
- [ ] لوحة تحكم (dashboard) تعمل
- [ ] نظام early warning فعال (tested)
- [ ] reports mechanism functional
- [ ] team trained (all operators)
- [ ] donor pipeline secured (first 500k NIS committed)
- [ ] legal/permits (if required by authorities)
- [ ] communication plan (community awareness)

---

**🦾 Manual مكتمل.  
كل سيناريو مذكور، كل أمر موجود.  
الآن: ابدأ بالخطوة 1 — التسجيل.**

---

**📞 للاستفسار:**  
0599123456 — أبو سالم (مدير الميدان)

🕌 "إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ"
