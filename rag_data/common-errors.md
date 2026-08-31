# Common Errors & Troubleshooting

## Error Code Reference
| Code | Meaning | Resolution |
|------|---------|------------|
| `INV-001` | Duplicate invoice number for this vendor | Check if the invoice was already posted; use a corrected invoice number if it's a genuine re-submission |
| `PO-404` | Purchase order not found | Verify the PO number; it may have been closed, cancelled, or belongs to a different company/branch |
| `WH-102` | Destination warehouse inactive | Confirm the warehouse status under Inventory > Warehouses before retrying the transfer |
| `AUTH-403` | Access denied | User lacks permission for this module/action — check Admin > Users > Permissions |
| `TAX-210` | Invalid or expired tax code | Update the tax code on the invoice line from Finance > Tax Codes |
| `QTY-301` | Invoiced quantity exceeds received quantity | Correct the goods receipt or request a manager override |
| `SYNC-500` | Integration sync failure with external system | Check Admin > Integrations > Sync Logs for the failed job and retry |

## General Troubleshooting Steps
1. **Reproduce the issue** — note the exact screen, action, and any error message text or code.
2. **Check permissions** — many "unexpected" errors are actually permission issues (see `AUTH-403`).
3. **Check related records** — most posting errors (invoices, POs, transfers) stem from a mismatch with a related record.
4. **Take a screenshot** — including the full error dialog and the screen behind it helps support diagnose faster.
5. **Check system status** — visit the status page for any ongoing incidents before filing a ticket.

## When to Escalate vs. Self-Resolve
- **Self-resolve**: Permission errors you can fix yourself, data entry mistakes, tax code updates.
- **Escalate (file a ticket)**: Error codes not in this reference, repeated failures after retrying, or anything affecting multiple users.

## Browser/Session Issues
Persistent "Session Expired" errors or blank screens are often resolved by clearing browser cache or trying an incognito/private window before filing a ticket.
