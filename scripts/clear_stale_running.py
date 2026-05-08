import json, time

state_file = '/root/.openclaw/cron/jobs-state.json'
with open(state_file, 'r') as f:
    s = json.load(f)

now = int(time.time() * 1000)
cleared = []

for jid, job in s.get('jobs', {}).items():
    st = job.get('state', {})
    running_at = st.get('runningAtMs', 0)
    if running_at:
        # If running flag is older than 5 minutes, assume stale and clear
        if now - running_at > 5 * 60 * 1000:
            job['state']['runningAtMs'] = None
            cleared.append(jid)
            print(f"Cleared stale running flag: {jid[:8]}...")
        else:
            print(f"Job {jid[:8]}... still running ({(now - running_at)/60000:.1f} min)")

print(f"\nCleared {len(cleared)} stale flags")
with open(state_file, 'w') as f:
    json.dump(s, f, indent=2)
print("jobs-state.json updated")
