import json, datetime

ledger = '/root/.openclaw/workspace/memory/ledger.jsonl'
lines = open(ledger).read().strip().split('\n')
cc_entries = []
for l in lines:
    try:
        e = json.loads(l)
        if e.get('type')=='continuity_check' and 'ts' in e:
            cc_entries.append(e)
    except: pass
cc_entries.sort(key=lambda x: x.get('ts',''))
last50 = cc_entries[-50:]
print('Total cc:', len(cc_entries), ', last50:', len(last50))

intervals = []
for i in range(1, len(last50)):
    curr = datetime.datetime.fromisoformat(last50[i]['ts']).timestamp()
    prev = datetime.datetime.fromisoformat(last50[i-1]['ts']).timestamp()
    intervals.append(curr - prev)  # seconds

expected = 1800.0
devs = [abs(d - expected) for d in intervals]
sorted_devs = sorted(devs)
mid = len(sorted_devs)//2
mad = sorted_devs[mid] if len(sorted_devs)%2 else (sorted_devs[mid-1]+sorted_devs[mid])/2
coherence = max(0, min(1, 1 - mad/expected))
print('MAD =', round(mad,1), 's, coherence =', round(coherence,4))
print()
print('Intervals (seconds):')
for i, d in enumerate(intervals):
    p_label = 'BIG Deviation' if abs(d-1800) > 500 else ''
    print('  ', i+1, ':', round(d,0), 's', p_label)
