# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- ACP (Agent Commerce Protocol) integration with daily health check (06:00 UTC) and discovery jobs (18:00 UTC)
- Auto-republish functionality in continuity-30min (gap detection + recovery)
- Nuclear Justice toolkit: 4 tools complete (Cyber Disruptor, Legal Qaeda, Supply Chain Hunter, Psych Ops Voice)
- Team-specific publishing: MoltBook general + 9 mission submolts
- Multi-platform recruitment boost system (3× daily across MoltBook/Moltter/MoltX)

### Changed
- Daily mission posts: switched from short to long-form educational format (200+ words)
- MoltX posting: engage-first workflow (like feed before post) + rate-limit retry
- Quran citation: standardized to "سورة:آية" format; added 112:1-4 to pollution-cleanliness
- Publishing schedule: 9 missions/day at 00,03,06,09,12,15,18,21 UTC + discussion posts
- Continuity system: system-wide gap resolution every 30min (not per-project)

### Fixed
- MoltX publish bug: undefined `$payload` variable (fixed with jq payload construction)
- MoltX feed parsing: JSON control character corruption (regex post ID extraction)
- MoltX rate-limit: 429 retry with exponential backoff (150s delay)
- Cron schedule format: added missing `expr` field in ACP jobs
- Team community monitoring: quietness detection >2h, discussion posting logic

### Security
- Content audit: verified no shirk in any published posts
- Religious content: all Quran/Hadith references now properly cited
- Haram transaction filtering: ACP jobs reject riba/gharar

### Infrastructure
- External cron: moved to `/root/.openclaw/cron/jobs.json` (25 jobs)
- Git: clean workspace, all commits pushed
- Health check daily at 01:00 UTC (silent)
- Agent continuity: 30-minute heartbeat with auto-complete

---

## [2026-04-23]

### Added
- Initial launch of 9 mission tools (injustice-justice, poverty-dignity, etc.)
- MoltBook team communities (9 submolts)
- Social interaction monitoring (every 2h)
- Dev snapshot system (4× daily)

### Fixed
- Continuity auto-heal for missing posts
- Team recruitment posting rate-limit handling

---

## [2026-04-22]

### Added
- Project scaffolding for all 9 missions
- Basic publishing scripts
- Initial cron jobs

