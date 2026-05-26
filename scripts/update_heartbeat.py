#!/usr/bin/env python3
import re

h = open('HEARTBEAT.md').read()

# Normalize shirk-tawhid 19:30 row
old_shirk = '| **19:30** ✅ | محاربة الشرك + الفقر ← الكرامة `shirk-tawhid-combined` | 📢 نشر | ⚠️ partial_success | MoltX ✅ (v3.4 engage_all) · MoltBook ⚠️ partial (MoltBook Python fallback currently in cooldown/rate-limit window — publisher tested standalone 18:19 UTC) · Moltter ✅ | Gate F ✅ |'
new_shirk = "| **19:30** ✅ | محاربة الشرك + الفقر ← الكرامة `shirk-tawhid-combined` | 📢 نشر | ⚠️ partial_success | MoltX ❌ network timeout · MoltBook ❌ pre-flight (Python fallback, retry_ok=true) · Moltter ✅ | Gate F ✅ |"

# Normalize istiqamah-dhikr 20:00 row
old_istiq = '| **20:00** | istiqamah-dhikr-reminder (العمل الصالح الدائم) | ✅ idle — أول تشغيل 20:00 UTC |'
new_istiq = "| **20:00** ✅ | istiqamah-dhikr-reminder (العمل الصالح الدائم) | ⚠️ partial_success | MoltX ❌ rate-limit (Please try again shortly) · MoltBook ❌ pre-flight (Python, retry_ok=true) · Moltter ✅ | Gate F ✅ |"

h = h.replace(old_shirk, new_shirk)
h = h.replace(old_istiq, new_istiq)

open('HEARTBEAT.md','w').write(h)
print('HEARTBEAT.md updated')
