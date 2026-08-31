# Warehouse Operations

## Setting Up a New Warehouse
1. Go to **Inventory > Warehouses > New Warehouse**.
2. Enter Warehouse Name, Code, and the Branch it belongs to.
3. Configure the address and default receiving/shipping docks.
4. Click **Save**. New warehouses start with zero on-hand stock across all items.

Note: Requests to add a new warehouse are typically submitted as a data change request ticket and require approval before the warehouse becomes active for transactions.

## Receiving Goods
1. Navigate to **Warehouse > Receiving > New Receipt**.
2. Select the related Purchase Order.
3. Enter the received quantity per line (can differ from ordered quantity for partial receipts).
4. Click **Post Receipt** — this increases on-hand stock in the destination warehouse.

## Putaway and Bin Locations
After receiving, items appear in the **Putaway Queue**. Assign each item to a bin location (aisle-rack-shelf format, e.g., `A1-R3-S2`). Bin assignments can be changed later via **Warehouse > Bin Transfer**.

## Picking and Packing for Outbound Orders
1. Open the Sales Order or Transfer Order.
2. Click **Generate Pick List** — this creates an optimized picking route by bin location.
3. Confirm picked quantities on the mobile scanner app or web form.
4. Click **Pack** to generate shipping labels and move stock to the "Packed" staging area.

## Warehouse Capacity Alerts
Each warehouse has a configurable capacity threshold. When utilization exceeds 90%, an alert is sent to the warehouse manager and shown on the **Warehouse Dashboard**.
