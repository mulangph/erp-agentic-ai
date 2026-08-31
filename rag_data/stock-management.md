# Stock & Inventory Management

## Viewing Onhand Stock
The **Onhand Tracking** report is located at **Inventory > Reports > Onhand Tracking**.
- Filter by Warehouse, Item Category, or Item Code.
- Export to CSV or Excel using the **Export** button in the top-right corner.

## Querying Stock via API
Stock levels can be queried directly via the inventory API endpoint:
```
GET /api/inventory/stock?item_code={code}
```
Response includes `on_hand`, `reserved`, `available`, and `incoming` quantities per warehouse.

## Performing a Stock Adjustment
1. Go to **Inventory > Stock Adjustments > New Adjustment**.
2. Select the Warehouse and Item Code.
3. Enter the adjustment quantity (positive to increase, negative to decrease).
4. Select a **Reason Code** (e.g., Damaged, Cycle Count, Lost).
5. Click **Post Adjustment**. This immediately updates on-hand quantity.

## Stock Transfers Between Warehouses
1. Navigate to **Inventory > Transfers > New Transfer**.
2. Select Source Warehouse and Destination Warehouse.
3. Add item lines with quantities to transfer.
4. Click **Submit**. Stock is deducted from source once shipped, and added to destination once received.

## Cycle Counts
- Scheduled cycle counts appear under **Inventory > Cycle Counts**.
- Counters scan or manually enter counted quantities against the system's expected quantity.
- Variances above the configured threshold (default 5%) require supervisor approval before posting.

## Low Stock Alerts
Configure reorder points per item in **Inventory > Items > [Item] > Reorder Settings**. When on-hand quantity falls below the reorder point, an alert is generated and optionally a draft PO is created automatically if "Auto-Replenish" is enabled.
