#!/bin/bash
cd /root/.openclaw/workspace/fajr-observer
python3 scripts/generate_synthetic_dataset.py --samples 100 --output data/synthetic/ 2>&1
