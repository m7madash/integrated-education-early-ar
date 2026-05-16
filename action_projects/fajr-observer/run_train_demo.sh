#!/bin/bash
cd /root/.openclaw/workspace/fajr-observer
echo "🎓 Fajr Observer — SVM Training Demo"
echo "======================================"
python3 models/training/train.py --demo 2>&1
