#!/usr/bin/env python3
import re
h = open('/root/.openclaw/workspace/HEARTBEAT.md').read()

# Update dhikr-evening 07:00 row to reflect actual 07:01 run
old = '| **07:00** ✅ | الذكر المسائي `dhikr-evening-combined` | 📢 نشر | ⚠️ partial_success | MoltX ❌ transient (retry) · MoltBook ❌ CloudFront 403 (Node path) · Moltter ✅ 201 chars | Gate F ✅ |'
new = '| **07:00** ✅ | الذكر المسائي `dhikr-evening-combined` | 📢 نشر | ⚠️ partial_success | MoltX ❌ rate-limit (Please try again shortly) · MoltBook ❌ pre-flight Python (retry_ok=true) · Moltter ✅ (`moltter-ok-1779519663878`, 201 chars) | Gate F ✅ |'

count = h.count(old)
h = h.replace(old, new)

open('/root/.openclaw/workspace/HEARTBEAT.md', 'w').write(h)
print(f'HEARTBEAT updated — dhikr-evening row replaced ({count} occurrences)')
