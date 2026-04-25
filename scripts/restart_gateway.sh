#!/bin/bash
# Restart OpenClaw Gateway — connectivity fix

echo "🔄 Restarting OpenClaw Gateway..."

# Stop gateway
openclaw gateway stop

# Wait
sleep 2

# Start gateway
openclaw gateway start

# Wait for startup
sleep 3

# Check status
openclaw status

echo ""
echo "✅ Gateway restarted."
echo "Verifying config..."
openclaw config validate || echo "⚠️ Config validation failed — check logs"

# Check memorySearch config
grep -A 5 "memorySearch" /root/.openclaw/openclaw.json

echo ""
echo "📋 Next: Run connectivity check manually:"
echo "  /root/.openclaw/workspace/action_projects/platform-connectivity-check/check_connectivity.sh"