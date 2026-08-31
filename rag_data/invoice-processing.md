# Invoice Processing

## Posting a Vendor Invoice
1. Go to **Accounts Payable > Invoices > New Invoice**.
2. Enter the Vendor Code — this must exactly match the vendor on the related Purchase Order.
3. Enter the Invoice Number as provided by the vendor (must be unique per vendor).
4. Match invoice lines to PO lines using the **Match to PO** button.
5. Verify Tax Codes on each line are valid for the vendor's jurisdiction.
6. Click **Post Invoice**.

## Common Invoice Posting Errors
- **Vendor code mismatch**: The vendor code on the invoice does not match the PO. Correct the vendor code or select the right PO.
- **Invalid tax code**: The tax code assigned to a line is not active for the vendor's region. Update the tax code from **Finance > Tax Codes**.
- **Duplicate invoice number**: The system detected the same invoice number already posted for this vendor (see error `INV-001`).
- **Quantity mismatch**: Invoiced quantity exceeds received quantity. Requires a manager override or a corrected receipt.

## Three-Way Matching
The system performs three-way matching between:
1. Purchase Order (what was ordered)
2. Goods Receipt (what was received)
3. Invoice (what was billed)

Discrepancies beyond the configured tolerance (default 2%) will block posting and route the invoice to **Exceptions > Matching Review**.

## Invoice Approval Workflow
Invoices above the auto-approval threshold (configurable per company, default $5,000) require manager sign-off under **Accounts Payable > Approvals** before payment can be scheduled.

## Crediting an Invoice
To issue a credit memo, open the original invoice and click **Create Credit Memo**. Adjust quantities or amounts being credited, then submit for approval.
