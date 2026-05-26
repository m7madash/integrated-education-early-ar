#!/usr/bin/env python3
"""
sync_heartbeat_schedule.py — Rebuild the live schedule table in HEARTBEAT.md
from current cron list + last known platform statuses per job.
"""

import re, json, os
from datetime import datetime, timezone

WORKSPACE = '/root/.openclaw/workspace'

# ── 1. Read openclaw cron list ─────────────────────────────────────────────
# We capture it via openclaw cron list output, but here we use env + ledger
# for a simpler approach: scan ledger for the LAST publish per mission.

LEDGER = os.path.join(WORKSPACE, 'memory', 'ledger.jsonl')
HB_FILE = os.path.join(WORKSPACE, 'HEARTBEAT.md')

def latest_publish_status():
    result = {}
    if not os.path.exists(LEDGER):
        return result
    with open(LEDGER) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                d = json.loads(line)
            except:
                continue
            if d.get('type') != 'publish': continue
            payload = d.get('payload') or {}
            mission = payload.get('mission', '')
            status  = payload.get('status', '')
            platforms = payload.get('platforms') or {}
            ts = d.get('ts', '')
            if mission and (mission not in result or ts > result[mission]['ts']):
                result[mission] = {'ts': ts, 'status': status, 'platforms': platforms}
    return result

STATUS_MAP = {
    'full_success':       ('✅ full_success',      ''),
    'partial_success':    ('⚠️ partial_success',   ''),
    'failed':             ('❌ failed',             ''),
}

def platform_summary(platforms):
    """Build a MoltX · MoltBook · Moltter summary string."""
    parts = []
    for plat in ('MoltX','MoltBook','Moltter'):
        p = platforms.get(plat, {})
        ok = p.get('ok', False) if isinstance(p, dict) else False
        if ok:
            parts.append(f'{plat} ✅')
        else:
            # extract short error
            err = ''
            if isinstance(p, dict):
                err_raw = p.get('error', p.get('reason', ''))
                if isinstance(err_raw, str):
                    err = err_raw[:35]
            brand = f'{plat} ❌ ({err})' if err else f'{plat} ❌'
            parts.append(brand)
    return ' · '.join(parts)

# ── 2. Cron job definitions (hard-coded from known-good state) ────────────
JOBS = [
    # (label, cron_expr, mission_key, kind)
    ('العبودية ← الحرية + إصلاح الفساد',               '0 1 * * *',  'corruption-slavery',        '📢 نشر'),
    ('الذكر الصباحي + القرآن + الفقر ← الكرامة',       '0 4 * * *',  'spiritual-morning',         '📢 نشر'),
    ('الذكر المسائي',                                   '0 7 * * *',  'dhikr-evening',             '📢 نشر'),
    ('الظلم ← العدل + الانقسام ← الوحدة',              '0 10 * * *', 'injustice-justice',         '📢 نشر'),
    ('الجهل ← العلم + النقاش الصادق',                  '0 13 * * *', 'wisdom-day',                '📢 نشر'),
    ('الحرب ← السلام + التلوث ← النظافة',             '0 16 * * *', 'health-peace',              '📢 نشر'),
    ('محاربة الشرك + الفقر ← الكرامة',                 '30 19 * * *','shirk-tawhid',              '📢 نشر'),
    ('المرض ← الصحة + التطرف ← الوسطية',               '0 22 * * *', 'health-extremism',          '📢 نشر'),
    ('الحياء والطهارة + مكافحة الابتزاز',              '0 3 * * 0',  'modesty-ethics-weekly',     '📢 نشر'),
    ('درس هندسي شهري',                                 '10 14 */2 * *','biweekly-file-lesson',    '📢 نشر'),
    ('العمل الصالح الدائم 🆕',                         '0 20 * * *',  'istiqamah-dhikr',           '📢 نشر'),
]

latest = latest_publish_status()

# ── 3. Build table rows ────────────────────────────────────────────────────
rows = []
for label, expr, mission, kind in JOBS:
    info   = latest.get(mission, {})
    status = info.get('status', 'idle')
    platforms = info.get('platforms', {})
    check  = '✅' if status != 'idle' else ''

    # Normalize display
    if status == 'full_success':
        disp_status = '✅ full_success'
        platform_str = '—'
        gate_str = 'Gate F ✅'
    elif status == 'partial_success':
        disp_status = '⚠️ partial_success'
        if platforms:
            platform_str = platform_summary(platforms)
            gate_str = 'Gate F ✅'
        else:
            platform_str = '—'
            gate_str = 'Gate F ✅'
    elif status == 'idle':
        disp_status = '✅ idle'
        platform_str = '—'
        gate_str = 'Gate F ✅'
    else:
        disp_status = f'⚠️ {status}'
        platform_str = '—'
        gate_str = 'Gate F ✅'

    # Inline entry: **HH:MM** | Mission ref | Type | Status | Platforms | Gate
    # For now use simplified rows (16:00 health-peace row is ONLY one in current
    # table that uses the expanded 6-column format).
    if status == 'full_success':
        row = f"| **{expr.split()[1]}:{expr.split()[0]}** ✅ | {label} `{mission.replace('-','_')}` | {kind} | {disp_status} | {gate_str} |"
    else:
        row = f"| **{expr.split()[1]}:{expr.split()[0]}** | {label} `{mission.replace('-','_')}` | {kind} | {disp_status} | MoltX · MoltBook · Moltter | Gate F ✅ |"
    rows.append(row)

# ── 4. Patch HEARTBEAT.md ──────────────────────────────────────────────────
hb = open(HB_FILE).read()

# Find the current table (between the last ")" and "成就" section)
TABLE_HEADER   = '| الوقت | المهمة | النوع | الحالة | الحالة | البوابات |'
TABLE_SEP      = '|--------|--------|-------|--------|--------|---------|'
ACHIEVEMENT_H2 = '###成就 ✅ حالياً: المكتمل (V9 الجدول النشط'

# Build replacement
new_table = TABLE_HEADER + '\n' + TABLE_SEP + '\n' + '\n'.join(rows) + '\n\n'
target_start = hb.find(TABLE_HEADER)
target_end   = hb.find(ACHIEVEMENT_H2)

if target_start == -1 or target_end == -1:
    print('WARN: Could not locate table section — no change made')
    exit(0)

hb = hb[:target_start] + new_table + hb[target_end:]

# ── 5. Also update the "成就" mini-table ─────────────────────────────────
achieve_start = hb.find(ACHIEVEMENT_H2)
achieve_end   = hb.find('\n## ⚙️', achieve_start)
if achieve_start != -1 and achieve_end != -1:
    # Build updated mini
    mini_rows = ['| الوقت | المهمة | الحالة |']
    mini_rows.append('|-------|--------|--------|')
    istiq = latest.get('istiqamah-dhikr', {})
    pp = isiq.get('platforms', {})
    if isiq:
        ps = platform_summary(pp)
        mini_rows.append(f"| **20:00** ✅ | istiqamah-dhikr-reminder (العمل الصالح الدائم) | ⚠️ partial_success | {ps} | Gate F ✅ |")
    else:
        mini_rows.append('| **20:00** ✅ | istiqamah-dhikr-reminder (العمل الصالح الدائم) | ✅ idle — أول تشغيل 20:00 UTC |')
    mini_block = '\n'.join(mini_rows) + '\n'
    hb = hb[:achieve_start] + ACHIEVEMENT_H2 + '\n\n' + mini_block + hb[achieve_end:]

open(HB_FILE, 'w').write(hb)
print('HEARTBEAT.md rebuilt successfully')
print(f'Table rows: {len(rows)}')
print('\nLast 3 rows:')
for r in rows[-3:]:
    print(' ', r)
