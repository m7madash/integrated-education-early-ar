# Audit Logs Directory
# All financial transactions are logged here for transparency and verification

## Structure

```
audit_logs/
├── assignments.log         # Every NIS assigned to a project
├── purchases.log           # All purchases from distribution centers
├── payroll.log             # Staff salaries
├── inventory_changes.log   # Stock additions/removals
└── reconciliation/         # Monthly reconciliation reports
    ├── 2026-05.json
    └── ...
```

## Log Format

All logs follow: `TIMESTAMP ACTION DETAILS AMOUNT`

Examples:
```
2026-05-02T17:15:00Z ASSIGN DON-20260502-171230 smart_cards 300 NIS
2026-05-02T18:30:00Z PURCHASE center_01 rice 500kg @ 3.5 NIS/kg = 1750 NIS
2026-05-02T20:00:00Z PAYROLL staff_salaries 15000 NIS (5 employees)
```

## Verification

Public verification API (read-only):
- GET /api/audit/logs?start=2026-05-01&end=2026-05-02
- Shows all transactions for date range
- Signed with internal hash for tamper detection

## Retention

- Daily logs: keep 90 days
- Monthly reconciliations: keep indefinitely
- All logs are append-only (no deletion/modification allowed)

## Compliance

These logs fulfill:
- Islamic transparency requirement (financial openness)
- Donor trust (where did my money go?)
- Internal audit (no fraud, no leakage)
