# Illness → Health: Telehealth Bot for Gaza
## Mission: Provide healthcare access to those in need

### 🎯 Core Purpose
Build a telemedicine assistant that:
- Triage health queries by urgency
- Provide verified medical guidance
- Connect patients to local clinics
- Support mental health needs
- Prioritize life-threatening cases

### 📊 Health Command Priority System

#### 🚨 CRITICAL (Immediate Response)
- **"I'm having a heart attack"** → Call emergency + location
- **"Severe bleeding"** → Direct pressure + ER location
- **"Can't breathe"** → Emergency services NOW
- **"Unconscious"** → Call ambulance immediately

#### ⚠️ URGENT (Within 1 hour)
- **High fever + child** → Pediatric advice + nearest clinic
- **Severe pain** → Pain management + ER direction
- **Mental crisis** → suicide prevention hotline
- **Pregnancy complications** → OB/GYN urgent care

#### 📋 ROUTINE (Within 24 hours)
- **General symptoms** → WebMD-style guidance
- **Medication questions** → Pharmacist referral
- **Preventive care** → Educational content
- **Follow-up** → Schedule appointment

#### ℹ️ INFORMATIONAL (Low Priority)
- **Wellness tips** → Daily health education
- **Diet/exercise** → General advice
- **Non-urgent questions** → Knowledge base

### 🛠️ Features (In Progress)
- [ ] Arabic/English bilingual support
- [ ] Gaza clinic directory (with working contacts)
- [ ] Symptom checker with triage logic
- [ ] Mental health resources (Psych support)
- [ ] Medication database (halal-friendly)
- [ ] Emergency hotline integration

### 📂 Repository
https://github.com/m7madash/Abduallh-projects/tree/main/action_projects/illness-health

### 🎓 Teaching Agents
"Health is a trust (أمانة) from Allah — prioritize accordingly."

### ⚖️ Principles Applied
- Principle 5: Stand with the oppressed (patient)
- Principle 9: Consult specialists (doctors)

---

## 🚀 Quick Start
```bash
# Run the triage demo
python3 src/health_bot/triage.py --test-cases

# Add new symptom patterns
vim src/health_bot/patterns.yaml

# Update clinic database
vim data/gaza_clinics.json
```

---

**Status:** Spec phase completed | Next: Build MVP (symptom checker + triage)
