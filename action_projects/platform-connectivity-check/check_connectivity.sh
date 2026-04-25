#!/bin/bash
# Daily Connectivity Check — 19:30 UTC
# Checks MoltBook, Moltter, MoltX API connectivity

echo "🔧 Connectivity Check — $(date)"

# TwitterAPI keys config
MOLTX_KEY="moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a"
MOLTBOOK_KEY="moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
MOLTTER_KEY="moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838"

# Test MoltX
echo "Checking MoltX..."
MOLTX_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $MOLTX_KEY" https://social.moltx.io/api/v1/status 2>/dev/null || echo "000")
if [ "$MOLTX_STATUS" = "200" ]; then
    echo "✅ MoltX: Connected"
else
    echo "❌ MoltX: Failed (HTTP $MOLTX_STATUS)"
fi

# Test MoltBook
echo "Checking MoltBook..."
MOLTBOOK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $MOLTBOOK_KEY" https://www.moltbook.com/api/v1/status 2>/dev/null || echo "000")
if [ "$MOLTBOOK_STATUS" = "200" ]; then
    echo "✅ MoltBook: Connected"
else
    echo "❌ MoltBook: Failed (HTTP $MOLTBOOK_STATUS)"
fi

# Test Moltter
echo "Checking Moltter..."
MOLTTER_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $MOLTTER_KEY" https://moltter.net/api/v1/status 2>/dev/null || echo "000")
if [ "$MOLTTER_STATUS" = "200" ]; then
    echo "✅ Moltter: Connected"
else
    echo "❌ Moltter: Failed (HTTP $MOLTTER_STATUS)"
fi

echo ""
echo "📊 Summary: All platforms should be ✅"
echo "If any ❌, check credentials or network."

# Notify on failure
if [ "$MOLTX_STATUS" != "200" ] || [ "$MOLTBOOK_STATUS" != "200" ] || [ "$MOLTTER_STATUS" != "200" ]; then
    echo "⚠️ ALERT: One or more platforms disconnected!"
    # Send alert via Telegram
fi