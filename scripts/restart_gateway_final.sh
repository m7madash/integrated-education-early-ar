#!/bin/bash
# Restart OpenClaw Gateway — load updated config

echo "🔄 Stopping OpenClaw Gateway..."
openclaw gateway stop

sleep 2

echo "✅ Starting OpenClaw Gateway..."
openclaw gateway start

sleep 3

echo ""
echo "📋 Gateway Status:"
openclaw status

echo ""
echo "🔍 Verifying config..."
if openclaw config validate; then
    echo "✅ Config validation passed"
else
    echo "❌ Config validation failed — check /root/.openclaw/logs/"
fi

echo ""
echo "🎯 Next step: Run connectivity check"
echo "  /root/.openclaw/workspace/action_projects/platform-connectivity-check/check_connectivity.sh"