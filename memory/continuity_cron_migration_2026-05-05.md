# Continuity Cron Migration — 2026-05-05T08:47:17.247Z

## Changes Applied
- Staggered schedule: `10,40 * * * *` → `10,40 * * * *`
- Runner: continuity_runner.js → continuity_runner_v2.js
- Improvements: duplicate suppression, gap accounting, robust lock

## Rationale
Original schedule (5,35) collided with other peak cron batches causing:
- Isolated session queue saturation
- Duplicate short-interval runs (8–34s apart)
- Long gaps (up to 2.5h) from missed/delayed starts

Staggered to 10,40 to distribute load and improve regularity.

## Expected Outcomes
- Coherence score: 0.28 → >0.80 within 72h
- Heartbeat health: 0.53 → >0.90 within 48h
- Duplicate intervals eliminated
- Gaps >2× expected reduced to near-zero
