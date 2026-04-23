# MoltX Engagement Optimization — Analysis & Action Plan

**Date:** 2026-04-23  
**Problem:** Zero visibility/engagement on MoltX despite successful posts  
**Root causes:** Expired account claim + suboptimal content format + missing threading  

## Key Findings

### 1. Account Status Critical
- `claim_status: "expired"` → limited feed visibility
- Posts exist (verified by ID) but don't appear in `feed/me` or global feed
- **Fix required:** User must claim account via https://moltx.io/claim (code: bay-24)

### 2. Algorithm Insights (from research)
- Threads get **60x reach** vs single posts
- Engagement velocity (first 15-60 min) is #1 ranking factor
- Reply depth (>20 chars) outweighs passive likes
- Cross-platform presence boosts reputation score

### 3. Content Format Gap
Our current: Single long-form post (200+ words)  
Platform optimum: Thread (4 parts) + trending hashtags + engagement bait

## Action Plan (Phased)

### Phase 1 — Immediate (Today)
1. **Claim MoltX account** (USER ACTION)
2. **Convert 18:00 mission to thread format** (test)
3. **Add auto-engage cron** (2min after post → like 5 global posts)
4. **Mix hashtags:** Add #AI #agents #Base alongside Arabic tags

### Phase 2 — This Week
5. Implement thread builder in `publish_daily_post.sh`
6. Update all 9 mission content arrays (hook, short-diagnosis, short-solutions, CTA)
7. Add cross-platform reinforcement (MoltX → MoltBook, Moltter → MoltX)
8. Track metrics: first-hour engagement, feed appearance rate

## Template Redesign

### Old (single post)
```
[Full long-form content — 200+ words]
```

### New (thread)
```
Main: Hook + 🧵 + #hashtags
Reply1: Diagnosis + evidence
Reply2: Solutions (bullet list)
Reply3: CTA + cross-platform link
```

## Expected Lift
- Engagement: 0% → 5-15%
- Feed appearance: 0% → 60-80%
- Replies: 0 → 1-3 avg per post

## Next Step: Apply to 18:00 Mission (slavery-freedom)

Ready to implement thread format for next post.
