# Reports

## Common Reports and Where to Find Them
| Report | Location |
|--------|----------|
| Onhand Tracking | Inventory > Reports > Onhand Tracking |
| Vendor Performance | Purchasing > Reports > Vendor Performance |
| Sales by Item | Sales > Reports > Sales by Item |
| Accounts Payable Aging | Finance > Reports > AP Aging |
| Accounts Receivable Aging | Finance > Reports > AR Aging |
| Cost Code Utilization | Finance > Reports > Cost Code Utilization |
| Warehouse Utilization | Inventory > Reports > Warehouse Utilization |

## Filtering and Exporting Reports
Most reports support filtering by:
- Date range (with quick presets like "Last 30 Days", "This Quarter")
- Warehouse or Branch
- Item Category or Cost Code

Click **Export** to download as CSV or Excel. Large reports (over 50,000 rows) are generated asynchronously and emailed as a download link.

## Scheduling Recurring Reports
1. Open the report and click **Schedule**.
2. Set frequency (Daily, Weekly, Monthly) and recipients.
3. Reports are emailed as an attachment at the scheduled time.

## Building a Custom Report
Advanced users can build custom reports at **Reports > Custom Report Builder** by selecting a data source (e.g., Purchase Orders, Invoices), choosing fields, and adding filters/groupings without writing SQL.

## Report Data Freshness
Most reports pull from a nightly-refreshed data warehouse, so figures may be up to 24 hours behind live transactional data. Reports explicitly labeled "Real-Time" query live data directly.
