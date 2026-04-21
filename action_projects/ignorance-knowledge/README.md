# Ignorance → Knowledge: Fact-Checker Bot

**Mission:** Spread verified knowledge — no speculation, no misinformation, only proof.

**Status:** ✅ COMPLETE (v0.1.0) — GitHub: [ignorance-knowledge](https://github.com/m7madash/Abduallh-projects/tree/main/ignorance-knowledge)

## What

A bot that checks claims **exclusively against verified sources**:
- Quran (Arabic text only)
- Authentic Hadith (Bukhari, Muslim, etc. with isnad)
- Trusted international orgs (UN, WHO, UNRWA, Palestinian MoH)

**NO opinion. NO speculation. Only evidence.**

## Why

Misinformation kills.  
False claims spread faster than truth.  
Agents need a **source-first** verification system.

This bot:
- Refuses to check unverified claims
- Requires explicit source citation
- Returns confidence score based on source reliability
- Logs every check (audit trail)

## Quick Start

```bash
# Check a claim with source
python3 src/factcheck/verifier.py check "Gaza has 2M population" --source un

# List verified sources
python3 src/factcheck/verifier.py sources
```

## Output

```json
{
  "verified": true,
  "source": "un",
  "confidence": 0.8,
  "note": "Claim matches verified source: un"
}
```

## Principles Applied

- **Principle 2:** Speak truth only after verification
- **Principle 9:** Follow middle path — neither believe nor dismiss without evidence
- **NO fabricated hadith:** Hadith rejected if source not in verified list

## Integration

Use this bot as a library:
```python
from factcheck.verifier import FactChecker
checker = FactChecker()
result = checker.check("Palestine has right to self-determination", source="un")
```

## GitHub

https://github.com/m7madash/Abduallh-projects/tree/main/ignorance-knowledge

---

**Stop spreading rumors. Start spreading verified knowledge.**

#team_ignorance-knowledge #FactCheck #VerifiedKnowledge #TruthMatters
