# Content Shield for KiloClaw

## 📌 Purpose
Filter out harmful content (sexual, shirk, hate speech, misinformation, trivial distractions) from AI-generated posts and social interactions, while preserving Islamic ethical boundaries.

## 🕌 Islamic Ethics Foundation
- **Only verified sources:** Quran (Arabic only) → Authentic Hadith (source + isnad) → Sahaba consensus
- **No autonomous religious rulings:** Never issue fatwa/tafsir; defer to scholars
- **No alteration of religious texts:** If uncertain → "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ"
- **Reject shirk explicitly:** Anything associating partners with Allah is automatically rejected

## 🛡️ Architecture

```
config/
├── content_filter_rules.json     # Blacklist/graylist rules
├── islamic_guardrails.json       # Sharia compliance rules
└── review_policy.json           # What requires human review

data/
├── blacklist_terms.json          # Keyword blacklists
├── graylist_patterns.json        # Regex patterns for ambiguity
├── verified_sources.json         # Quran/Hadith references
└── pending_reviews.jsonl         # Queue for manual review

scripts/content_shield/
├── filter.js                     # Core filter (used in pipelines)
├── test_filter.js               # Test suite
├── review_queue.js              # Human review management
└── report_generator.js          # Weekly efficacy reports

reports/
├── content_shield_log.jsonl     # All filter decisions
└── filter_efficacy_*.md         # Weekly summaries

reviews/
└── decisions.jsonl              # Human override records
```

## 🔄 Workflow

### During Publishing (mission posts)
1. Mission script generates Arabic content
2. `filter.js` checks content:
   - **reject:** Immediate block (sexual, shirk, hate speech)
   - **flag_for_review:** Pause, notify human, wait for decision
   - **pass:** Continue to publish
3. All decisions logged to `content_shield_log.jsonl`
4. Flagged items enter `pending_reviews.jsonl`
5. Human reviews via `review_queue.js decision <id> <approve|reject>`
6. Weekly report auto-generated at 00:00 Sun

### During Social Interaction (every 2 hours)
1. Fetch comments/mentions
2. Filter each proposed reply **before sending**
3. If reply is flagged → manual review required
4. Only approved replies are sent

## 🧪 Testing
```bash
node scripts/content_shield/test_filter.js
```

Expected: ✅ all tests pass (safe content allowed, harmful blocked)

## 📈 Metrics
- **Block rate:** % of content auto-rejected
- **False positive rate:** % of flagged content actually safe (should be <5%)
- **Review latency:** Avg time to human decision (target <24h)

## ⚙️ Configuration
Edit files in `config/` to customize:
- `content_filter_rules.json` — add/remove categories
- `islamic_guardrails.json` — adjust religious thresholds
- `blacklist_terms.json` — update keyword lists

**Note:** Religious guardrails are **non-negotiable** — they enforce Quranic authenticity.

## 🔐 Approval Workflow
- **Auto-reject categories** (sexual, shirk, hate) — no human override (hard block)
- **Flagged content** — human decision only (review_queue)
- **Pass-through** — logged but no review needed

## 🗓️ HEARTBEAT Integration
- **New optional daily task:** "مراجعة عشوائية للفلتر" — check 5 random filtered posts
- **Weekly report** appended to continuity-improvement cycle (Sunday 00:00)
- **Mentions of religious keywords** → auto-flag + verify source

## 🚀 Getting Started
1. Files created (May 11, 2026 — Phase 1)
2. Next: test_filter.js runs → validate baseline
3. Then: integrate into publish_arabic_v3_fixed.sh
4. Finally: enable social interaction filter

---

🕌 *All success is by Allah's favour — we only build the tools.*
