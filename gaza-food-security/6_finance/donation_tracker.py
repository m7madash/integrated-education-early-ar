#!/usr/bin/env python3
"""
Donation Tracker for Gaza Food Security
Tracks all incoming donations, assigns to projects, generates receipts
"""

import json
import os
from datetime import datetime, timezone

WORKSPACE = '/root/.openclaw/workspace/gaza-food-security'
DONATIONS_FILE = f'{WORKSPACE}/6_finance/donations.json'
RECEIPTS_DIR = f'{WORKSPACE}/6_finance/receipts'

# Ensure files exist
os.makedirs(os.path.dirname(DONATIONS_FILE), exist_ok=True)
os.makedirs(RECEIPTS_DIR, exist_ok=True)

if not os.path.exists(DONATIONS_FILE):
    with open(DONATIONS_FILE, 'w') as f:
        json.dump({"donations": []}, f, indent=2)

def record_donation(donor_name, donor_phone, amount_nis, payment_method, purpose="general", notes=""):
    """Record a new donation and generate receipt"""
    
    donation_id = f"DON-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    donation = {
        "donation_id": donation_id,
        "donor_name": donor_name,
        "donor_phone": donor_phone,
        "amount_nis": amount_nis,
        "payment_method": payment_method,  # cash, bank_transfer, crypto, etc.
        "purpose": purpose,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "received",
        "receipt_generated": False,
        "assigned_to_project": None,
        "spent_nis": 0,
        "remaining_nis": amount_nis
    }
    
    # Append to donations DB
    with open(DONATIONS_FILE, 'r+') as f:
        data = json.load(f)
        data["donations"].append(donation)
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Generate receipt
    generate_receipt(donation)
    
    print(f"✅ Donation recorded: {donation_id}")
    print(f"   Amount: {amount_nis} NIS")
    print(f"   Donor: {donor_name}")
    print(f"   Receipt: {RECEIPTS_DIR}/{donation_id}.txt")
    
    return donation_id

def generate_receipt(donation):
    """Create a human-readable receipt"""
    receipt_path = f"{RECEIPTS_DIR}/{donation['donation_id']}.txt"
    
    content = f"""🕌 مشروع غزة الغذائي — إيصال تبرع
==========================================
رقم الإيصال: {donation['donation_id']}
التاريخ: {donation['timestamp']}
==========================================
اسم المتبرع: {donation['donor_name']}
رقم الهاتف: {donation['donor_phone']}
طريقة الدفع: {donation['payment_method']}
المبلغ: {donation['amount_nis']} شيكل
الغرض: {donation['purpose']}
ملاحظات: {donation['notes']}
==========================================
✅ تم استلام المبلغ بموجب هذا الإيصال
التبرعات تُستخدم وفقاً للضوابط الشرعية:
  - العدالة في التوزيع
  - الشفافية الكاملة
  - لا ربا ولا غرر
==========================================
للاستفسار: 0599123456
"""
    with open(receipt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    donation['receipt_generated'] = True
    return receipt_path

def assign_donation(donation_id, project_name, amount):
    """Assign a donation to a specific project/phase"""
    with open(DONATIONS_FILE, 'r+') as f:
        data = json.load(f)
        
        for d in data["donations"]:
            if d["donation_id"] == donation_id:
                if amount > d["remaining_nis"]:
                    raise ValueError("Amount exceeds remaining balance")
                
                d["assigned_to_project"] = project_name
                d["spent_nis"] += amount
                d["remaining_nis"] -= amount
                
                # Log assignment
                log_assignment(donation_id, project_name, amount)
                print(f"✅ Assigned {amount} NIS from {donation_id} to {project_name}")
                break
        
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_assignment(donation_id, project, amount):
    """Log every assignment for audit"""
    log_file = f"{WORKSPACE}/6_finance/audit_logs/assignments.log"
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} ASSIGN {donation_id} -> {project} : {amount} NIS\n")

def get_financial_summary():
    """Generate executive summary of finances"""
    with open(DONATIONS_FILE) as f:
        data = json.load(f)
    
    total_donations = sum(d["amount_nis"] for d in data["donations"])
    total_spent = sum(d["spent_nis"] for d in data["donations"])
    total_remaining = total_donations - total_spent
    
    # By project
    by_project = {}
    for d in data["donations"]:
        if d["assigned_to_project"]:
            proj = d["assigned_to_project"]
            if proj not in by_project:
                by_project[proj] = 0
            by_project[proj] += d["spent_nis"]
    
    return {
        "total_donations_nis": total_donations,
        "total_spent_nis": total_spent,
        "total_remaining_nis": total_remaining,
        "by_project": by_project,
        "donation_count": len(data["donations"]),
        "as_of": datetime.now(timezone.utc).isoformat()
    }

def search_donations_by_donor(donor_name):
    """Find all donations from a specific person"""
    with open(DONATIONS_FILE) as f:
        data = json.load(f)
    
    return [d for d in data["donations"] if donor_name.lower() in d["donor_name"].lower()]

def generate_monthly_report(month_str):
    """Generate report for a specific month (YYYY-MM format)"""
    with open(DONATIONS_FILE) as f:
        data = json.load(f)
    
    monthly = [d for d in data["donations"] if d["timestamp"].startswith(month_str)]
    
    total = sum(d["amount_nis"] for d in monthly)
    spent = sum(d["spent_nis"] for d in monthly)
    
    report = {
        "month": month_str,
        "donation_count": len(monthly),
        "total_nis": total,
        "spent_nis": spent,
        "remaining_nis": total - spent,
        "top_donors": sorted(monthly, key=lambda x: x["amount_nis"], reverse=True)[:5]
    }
    
    # Save report
    report_file = f"{WORKSPACE}/6_finance/reports/monthly_{month_str}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

if __name__ == '__main__':
    # CLI interface
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: donation_tracker.py {record|assign|summary|search|monthly} [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "record":
        # donation_tracker.py record "أبو محمد" 0599123456 500 "cash" "general" "صدقة"
        name = sys.argv[2]
        phone = sys.argv[3]
        amount = float(sys.argv[4])
        method = sys.argv[5]
        purpose = sys.argv[6] if len(sys.argv) > 6 else "general"
        notes = sys.argv[7] if len(sys.argv) > 7 else ""
        record_donation(name, phone, amount, method, purpose, notes)
    
    elif cmd == "assign":
        # donation_tracker.py assign DON-20260502-171230 "smart_cards" 300
        donation_id = sys.argv[2]
        project = sys.argv[3]
        amount = float(sys.argv[4])
        assign_donation(donation_id, project, amount)
    
    elif cmd == "summary":
        summary = get_financial_summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    elif cmd == "search":
        # donation_tracker.py search "أبو محمد"
        donor = sys.argv[2]
        results = search_donations_by_donor(donor)
        for r in results:
            print(f"{r['donation_id']}: {r['amount_nis']} NIS — {r['purpose']}")
    
    elif cmd == "monthly":
        # donation_tracker.py monthly 2026-05
        month = sys.argv[2]
        report = generate_monthly_report(month)
        print(f"Month: {report['month']}")
        print(f"Donations: {report['donation_count']} totaling {report['total_nis']} NIS")
        print(f"Spent: {report['spent_nis']} NIS")
        print(f"Remaining: {report['remaining_nis']} NIS")
