#!/bin/bash
# Agent Performance Check - Every 4 hours
# Checks: Success rate, Errors, Fixes, Health status

echo "=== Agent Performance Report ==="
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check 1: OpenClaw status
echo "1. OpenClaw System Status:"
openclaw status 2>&1 || echo "  ⚠️  Status check failed"
echo ""

# Check 2: Recent session errors (last 4 hours)
echo "2. Errors in last 4 hours:"
find /root/.openclaw/workspace/memory -name "*.md" -mmin -240 -exec grep -i "error\|fail\|exception" {} \; 2>/dev/null | head -5 || echo "  ✅ No errors detected"
echo ""

# Check 3: Cron jobs health
echo "3. Cron Job Health:"
openclaw cron list 2>&1 | grep -E "(error|fail|stopped)" || echo "  ✅ All cron jobs running"
echo ""

# Check 4: Agent memory growth (should be normal)
echo "4. Memory Usage:"
du -sh /root/.openclaw/workspace/memory 2>/dev/null || echo "  N/A"
echo ""

# Check 5: Subagent completion rate
echo "5. Subagent Success Rate (last 24h):"
find /root/.openclaw/workspace/memory -name "*.md" -mmin -1440 -exec grep -c "completed successfully" {} \; 2>/dev/null | awk '{s+=$1} END {print "  ✅ "s+" successful tasks"}'
echo ""

# Auto-fix: Clear old temp files if disk usage high
DISK_USAGE=$(df /root | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  High disk usage detected ($DISK_USAGE%). Cleaning temp files..."
    find /tmp -name "openclaw_*" -mtime +1 -delete 2>/dev/null
    echo "  ✅ Cleanup complete"
fi

echo ""
echo "=== Report Complete ==="
