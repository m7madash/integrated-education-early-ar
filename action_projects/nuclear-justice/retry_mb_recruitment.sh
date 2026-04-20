#!/bin/bash
# Retry MoltBook recruitment post after rate limit (130 sec)
sleep 130
python3 /root/.openclaw/workspace/action_projects/nuclear-justice/publish_mb_recruitment.py
