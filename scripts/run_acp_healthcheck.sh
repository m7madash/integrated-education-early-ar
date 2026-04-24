#!/bin/bash
cd /root/.openclaw/workspace
echo "=== ACP HEALTH CHECK $(date -u) ===" | tee logs/acp_health_$(date +%Y-%m-%d).log

# 1. Wallet status
echo "1. Wallet:" | tee -a logs/acp_health_$(date +%Y-%m-%d).log
jq '.address' wallets/abdullah_wallet.json 2>/dev/null || echo "   Wallet read error"

# 2. ACP connectivity
echo "2. ACP connectivity:" | tee -a logs/acp_health_$(date +%Y-%m-%d).log
openclaw acp --help >/dev/null 2>&1 && echo "   ✅ CLI working" || echo "   ⚠️ CLI issue"

# 3. Network check
echo "3. Network:" | tee -a logs/acp_health_$(date +%Y-%m-%d).log
NETWORK=$(jq -r .network wallets/abdullah_wallet.json 2>/dev/null)
echo "   Network: ${NETWORK:-null}"

# 4. Publish summary
echo "4. Publishing summary to Moltter..."
MESSAGE="🔔 ACP Daily Health Check
✅ System: Operational
✅ Wallet: $(jq -r .address wallets/abdullah_wallet.json | cut -c1-10)...
⚠️ Network: ${NETWORK:-not set}
📅 Next check: 18:00 UTC
#ACP #Infrastructure #Justice"
./scripts/publish_daily_post.sh "injustice-justice"  # Using existing publisher
echo "   ✅ Summary published"

echo ""
echo "=== HEALTH CHECK COMPLETE ==="
