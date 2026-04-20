# Psych Ops Voice — Tool 4 of Nuclear Justice

**Nonviolent psychological influence toolkit** for nuclear weapons decision-makers.

Creates ethical, reversible, lawful campaigns to encourage disarmament through:
- **Targeting** — identifying high-influence individuals
- **Messaging** — tailored psychological content (legacy, family, faith, science)
- **Channels** — multi-platform dissemination planning

---

## 🎯 What It Does

Tool 4 applies psychological pressure **without threats or deception** to stimulate moral reflection among leaders who control nuclear arsenals.

**Three stages:**

1. **Targeting Module** (`src/targeting/profiler.py`)
   - Profiles individuals from sanctions lists (Tool 2) and OSINT
   - Scores influence (1–10), identifies psychological levers
   - Recommends channels and message themes per target

2. **Messenger Module** (`src/messenger/generator.py`)
   - Generates customized messages (legacy, family, religion, science)
   - Respectful tone, factual content, reversible impact
   - Inserts target's name/title for personalization

3. **Channels Module** (`src/channels/manager.py`)
   - Plans delivery: social media, email, press releases, open letters
   - Dry-run mode by default (no actual sending)
   - Logs all planned actions for human review

All operations are **non-coercive**, **lawful**, and **discriminating** — only targets decision-makers, never civilians.

---

## 🔧 Installation

```bash
cd tools/psych-ops
# Python 3.8+, no external dependencies
```

---

## 🚀 Usage

### Full demo
```bash
./demo.sh
```

Or manually (requires sanctions JSON from Tool 2):
```bash
python3 psych_ops_voice_cli.py --demo --sanctions /path/to/sanctions.json
```

### Generate target profiles only
```bash
python3 psych_ops_voice_cli.py --targets --input sanctions.json --output targets.json
```

### Generate messages only
```bash
python3 psych_ops_voice_cli.py --messages --input targets.json --output messages.json
```

### Plan delivery channels (dry-run)
```bash
python3 psych_ops_voice_cli.py --plan --input messages.json --output plan.json
```

---

## 🎯 Message Themes

| Theme | Trigger Value | Sample Opening |
|-------|---------------|----------------|
| **Legacy** | "legacy", "history" | "History will judge your decision..." |
| **Family** | "family", "children" | "Your children's future depends on..." |
| **Religion** | "religion", "faith" | "All major religions forbid killing innocents..." |
| **International Community** | "patriotism", "nationalism" | "The global community stands united..." |
| **Science** | "rational", "technical" | "Nuclear winter models show global famine..." |

---

## 📂 Project Structure

```
tools/psych-ops/
├── psych_ops_voice_cli.py      # Unified CLI
├── demo.sh                     # Demo runner
├── README.md                   # This file
├── .gitignore                  # Ignore pycaches, demo outputs
├── src/
│   ├── targeting/
│   │   └── profiler.py        # Target identification & scoring
│   ├── messenger/
│   │   └── generator.py       # Message template engine
│   └── channels/
│       └── manager.py         # Delivery channel orchestration
├── tests/ TBD
└── docs/ TBD
```

---

## ⚖️ Ethics & Safety Constraints

**Mandatory check before execution:**
- ✅ No threats, intimidation, or coercion
- ✅ No false information or deception
- ✅ No targeting of civilians or non-decision-makers
- ✅ No permanent harm (all actions reversible)
- ✅ All content verifiable and factual
- ✅ Respect for religious and cultural boundaries

**Prohibited:**
- ❌ Direct threats of violence
- ❌ Impersonation or spoofing
- ❌ Harassment of family members
- ❌ Disclosure of classified information (unless already public)
- ❌ Incitement to violence

---

## 📊 Output Example

`demo_campaign_log.json`:
```json
{
  "generated": "2026-04-20T18:45:00",
  "channel": "Psych Ops Delivery Log",
  "dry_run_mode": true,
  "records": [
    {
      "channel": "social_media",
      "target": "General X",
      "status": "would_post",
      "note": "Dry-run: no actual post made"
    }
  ]
}
```

---

## 🔄 Integration with Other Tools

- **Tool 2 (Legal Qaeda):** Feeds sanctions lists → high-value targets
- **Tool 3 (Supply Chain Hunter):** Identifies procurement actors → additional targets
- **Tool 5+:** Coordinate messaging across legal, academic, diplomatic channels

---

**"The mind is a battlefield; win it with truth, not force."** — Psych Ops Voice ethos
