import json, time
s = json.load(open('/root/.openclaw/cron/jobs-state.json'))
job_id = 'ea19561d-f2c2-4716-9032-5053e9f65dc3'
job = s['jobs'].get(job_id)
if job:
    print("State:", job)
    now = int(time.time()*1000)
    print("Now ms:", now)
    print("Next run ms:", job['state'].get('nextRunAtMs'))
    print("Last run ms:", job['state'].get('lastRunAtMs'))
    next_ms = job['state'].get('nextRunAtMs', 0)
    if next_ms:
        print("Next in", (next_ms - now)/60000, "minutes")
else:
    print("Job not found in state")
