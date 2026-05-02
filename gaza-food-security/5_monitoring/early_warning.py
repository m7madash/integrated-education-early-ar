#!/usr/bin/env python3
"""
Early Warning System for Gaza Food Security
Monitors stock levels and triggers alerts when thresholds are breached
"""

import json
import os
import requests
from datetime import datetime, timedelta

WORKSPACE = '/root/.openclaw/workspace/gaza-food-security'
CENTERS_FILE = f'{WORKSPACE}/2_smart_distribution/centers.json'
ALERT_LOG = f'{WORKSPACE}/5_monitoring/alerts.log'

# Thresholds (kg)
CRITICAL_THRESHOLD = 100   # Immediate restock needed
WARNING_THRESHOLD = 300   # Plan restock soon

# Admin contacts (would be real phone numbers/emails in production)
ADMIN_PHONE = '+972599123456'  # Simulated
ADMIN_EMAIL = 'admin@gaza-food.org'

def load_centers():
    with open(CENTERS_FILE) as f:
        data = json.load(f)
    return data['centers']

def check_stock(center):
    alerts = []
    for item, qty in center['inventory'].items():
        if qty < CRITICAL_THRESHOLD:
            alerts.append({
                'severity': 'critical',
                'item': item,
                'current': qty,
                'threshold': CRITICAL_THRESHOLD,
                'center': center['center_id'],
                'message': f"⚠️ CRITICAL: {item} at {qty}kg in {center['name']} — reorder NOW"
            })
        elif qty < WARNING_THRESHOLD:
            alerts.append({
                'severity': 'warning',
                'item': item,
                'current': qty,
                'threshold': WARNING_THRESHOLD,
                'center': center['center_id'],
                'message': f"⚠️ WARNING: {item} low ({qty}kg) at {center['name']} — schedule restock"
            })
    return alerts

def send_alert(alert):
    """Log alert and simulate sending to admin"""
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} [{alert['severity'].upper()}] {alert['message']}\n"
    
    with open(ALERT_LOG, 'a') as f:
        f.write(log_entry)
    
    # In production: send SMS/email/telegram
    print(f"ALERT: {alert['message']}")
    # Example: send_telegram_message(alert['message'])
    
def auto_reorder(alert):
    """For critical items, automatically create purchase order"""
    if alert['severity'] != 'critical':
        return
    
    # In production: this would create a PO in the procurement system
    print(f"🔄 Auto-reorder triggered for {alert['item']} at center {alert['center']}")
    # log to reorder_orders.json

def check_all_centers():
    centers = load_centers()
    all_alerts = []
    
    for center in centers:
        alerts = check_stock(center)
        all_alerts.extend(alerts)
    
    # Sort by severity
    all_alerts.sort(key=lambda x: 0 if x['severity']=='critical' else 1)
    
    # Send alerts (deduplicated by item+center)
    seen = set()
    for alert in all_alerts:
        key = f"{alert['center']}_{alert['item']}"
        if key not in seen:
            send_alert(alert)
            if alert['severity'] == 'critical':
                auto_reorder(alert)
            seen.add(key)
    
    return len(all_alerts)

if __name__ == '__main__':
    alert_count = check_all_centers()
    print(f"✅ Early warning check complete. {alert_count} alerts generated.")
    
    # Also write status for dashboard
    status = {
        'timestamp': datetime.now().isoformat(),
        'alerts_count': alert_count,
        'next_run': (datetime.now() + timedelta(hours=6)).isoformat()
    }
    with open(f'{WORKSPACE}/5_monitoring/ew_status.json', 'w') as f:
        json.dump(status, f, indent=2)
