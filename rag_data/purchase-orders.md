# Purchase Orders

## Creating a Purchase Order
1. Navigate to **Purchasing > Purchase Orders > New PO**.
2. Select the **Vendor** from the dropdown (type-ahead search supported).
3. Enter the **PO Date** and expected **Delivery Date**.
4. Click **Add Line** to add items:
   - Item Code
   - Quantity
   - Unit Price
   - Warehouse (destination)
5. Review the **Total** field, which auto-calculates from all lines plus tax.
6. Click **Submit for Approval**.

## Adding a Purchase Order Line
To add a line to an existing PO:
1. Open the PO from **Purchasing > Purchase Orders > Open PO**.
2. Click **Add Line**.
3. Enter the item code, quantity, and unit price.
4. Click **Save Line**, then **Save PO**.

## Editing a Purchase Order
- POs in **Draft** status can be edited freely.
- POs in **Pending Approval** require the approver to reject it back to Draft first.
- POs that are **Approved** and have received partial deliveries cannot have their quantities reduced below what has already been received.

## Approving a Purchase Order
1. Go to **Purchasing > Approvals**.
2. Select the PO and review the line items and total.
3. Click **Approve** or **Reject** (rejection requires a comment).

## Common PO Fields
| Field | Description |
|-------|-------------|
| Vendor | The supplier fulfilling the order |
| PO Number | Auto-generated, format `PO-YYYY-NNNNN` |
| Date | Date the PO was created |
| Lines | Item, Quantity, Price for each product ordered |
| Total | Sum of all lines including applicable tax |

## Closing a Purchase Order
A PO automatically closes when all lines are fully received and invoiced. To manually close a PO with partial delivery, go to the PO detail page and click **Force Close** (requires manager permission).
