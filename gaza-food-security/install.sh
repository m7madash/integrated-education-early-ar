#!/bin/bash
# Gaza Food Security — Installation Script
# Runs initial setup for the project

set -e

WORKSPACE="/root/.openclaw/workspace/gaza-food-security"
cd "$WORKSPACE"

echo "🕌 Installing Gaza Food Security System..."

# Create necessary directories
mkdir -p logs backups

# Initialize database files if they don't exist
if [ ! -f "1_assessment/families_register.json" ]; then
  echo '{"families": []}' > "1_assessment/families_register.json"
  echo "✅ Created families database"
fi

if [ ! -f "2_smart_distribution/cards_database.json" ]; then
  echo '{"cards": []}' > "2_smart_distribution/cards_database.json"
  echo "✅ Created cards database"
fi

if [ ! -f "2_smart_distribution/transactions.log" ]; then
  touch "2_smart_distribution/transactions.log"
  echo "✅ Created transaction log"
fi

if [ ! -f "4_recycling/collection.log" ]; then
  touch "4_recycling/collection.log"
  echo "✅ Created recycling log"
fi

if [ ! -f "5_monitoring/alerts.log" ]; then
  touch "5_monitoring/alerts.log"
  echo "✅ Created alerts log"
fi

# Create sample waste source bins for recycling
mkdir -p "4_recycling/waste_sources"
cat > "4_recycling/waste_sources/hotel_central/info.json" <<EOF
{
  "type": "organic_kitchen",
  "contact": "أبو محمد",
  "phone": "0599123456",
  "location": "فندق فلسطين، وسط المدينة",
  "collection_schedule": "daily 18:00"
}
EOF
touch "4_recycling/waste_sources/hotel_central/.keep"

cat > "4_recycling/waste_sources/market_souq/info.json" <<EOF
{
  "type": "organic_kitchen",
  "contact": "أبو خالد",
  "phone": "0598123456",
  "location": "سوق الزيتون",
  "collection_schedule": "daily 19:00"
}
EOF
touch "4_recycling/waste_sources/market_souq/.keep"

# Set permissions
chmod +x *.sh
chmod +x 1_assessment/*.sh
chmod +x 2_smart_distribution/*.sh
chmod +x 3_local_production/*.sh 2>/dev/null || true
chmod +x 4_recycling/*.sh
chmod +x 5_monitoring/*.py

# Create simple API endpoint for dashboard
mkdir -p "5_monitoring/api"
cat > "5_monitoring/api/metrics.py" <<'PYEOF'
#!/usr/bin/env python3
import json
import os
from datetime import datetime

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json(path):
    with open(path) as f:
        return json.load(f)

def count_lines(path):
    if not os.path.exists(path):
        return 0
    with open(path) as f:
        return sum(1 for _ in f)

def get_metrics():
    families = load_json(f"{WORKSPACE}/1_assessment/families_register.json")
    cards = load_json(f"{WORKSPACE}/2_smart_distribution/cards_database.json")
    centers = load_json(f"{WORKSPACE}/2_smart_distribution/centers.json")
    
    # Calculate hunger rate (simulated: families with priority score >=10 considered at risk)
    at_risk = sum(1 for f in families.get('families', []) if f.get('priority_score', 0) >= 10)
    total_families = len(families.get('families', []))
    hunger_rate = at_risk / total_families if total_families > 0 else 0
    
    # Total inventory across centers
    total_inventory_kg = 0
    for center in centers.get('centers', []):
        for qty in center.get('inventory', {}).values():
            total_inventory_kg += qty
    
    # Total card value
    total_card_value = sum(c.get('monthly_allocation_nis', 0) for c in cards.get('cards', []))
    
    # Recent distributions (simulate from transaction log)
    tx_log = f"{WORKSPACE}/2_smart_distribution/transactions.log"
    recent_tx = []
    if os.path.exists(tx_log):
        with open(tx_log) as f:
            lines = f.readlines()[-10:]  # last 10
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 6 and parts[1] == 'PURCHASE':
                recent_tx.append({
                    'date': parts[0],
                    'center': 'unknown',
                    'families': 1,
                    'kg': 0,  # not tracked in simple version
                    'nis': float(parts[-1])
                })
    
    # Financials (simulate)
    donations = 150000  # Would come from donation_tracker
    expenses = 95000
    balance = donations - expenses
    
    return {
        'timestamp': datetime.now().isoformat(),
        'families_registered': total_families,
        'hunger_rate': round(hunger_rate, 3),
        'inventory_tons': total_inventory_kg / 1000,
        'cards_value_nis': total_card_value,
        'local_production_percent': 0.15,  # TODO: calculate from actual data
        'centers_active': len(centers.get('centers', [])),
        'recent_distributions': recent_tx,
        'finance': {
            'donations_nis': donations,
            'expenses_nis': expenses,
            'balance_nis': balance
        },
        'alerts': []  # would come from early_warning system
    }

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--format':
        print(json.dumps(get_metrics(), indent=2, ensure_ascii=False))
    else:
        # CGI-like output for web server
        print("Content-Type: application/json\n")
        print(json.dumps(get_metrics()))
PYEOF
chmod +x "5_monitoring/api/metrics.py"

echo "✅ Installation complete!"
echo ""
echo "📌 Next steps:"
echo "1. Register families: ./1_assessment/register_family.sh FAM001 6 3 1 1500 0599123456"
echo "2. Start dashboard: cd 5_monitoring && python3 -m http.server 8080"
echo "3. View dashboard: http://localhost:8080/dashboard.html"
echo ""
echo "🕌 System ready. May Allah accept this work."
