import requests
import logging
from typing import Dict, Any, Optional
from erp_helpdesk.config import config

logger = logging.getLogger(__name__)

class ERPAPIClient:
    """Client for interacting with the ERP system's REST API."""
    
    def __init__(self):
        self.base_url = config.erp_api_base_url
        self.api_key = config.erp_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Mock data for testing if API is not available
        self.mock_data = {
            "inventory": {
                "CEMENT-001": {"item": "Cement", "stock": 1500, "warehouse": "Main"},
                "STEEL-002": {"item": "Steel Bars", "stock": 850, "warehouse": "Main"},
                "PAINT-003": {"item": "Industrial Paint", "stock": 320, "warehouse": "Secondary"},
                "BOLT-004": {"item": "Hex Bolts", "stock": 5000, "warehouse": "Main"},
                "WIRE-005": {"item": "Copper Wire", "stock": 1200, "warehouse": "Secondary"},
            },
            "vendors": {
                "CEMENT-001": [
                    {"name": "ABC Cement Co", "rating": 4.8, "lead_time": 3},
                    {"name": "XYZ Builders", "rating": 4.2, "lead_time": 5},
                    {"name": "Super Cement Ltd", "rating": 4.5, "lead_time": 4},
                ],
                "STEEL-002": [
                    {"name": "Steel Masters Inc", "rating": 4.9, "lead_time": 7},
                    {"name": "Metal Works Co", "rating": 4.3, "lead_time": 10},
                ],
            },
            "sales": {
                "CEMENT-001": [
                    {"date": "2026-08-28", "units": 500, "revenue": 25000},
                    {"date": "2026-08-27", "units": 450, "revenue": 22500},
                    {"date": "2026-08-26", "units": 600, "revenue": 30000},
                ],
                "STEEL-002": [
                    {"date": "2026-08-28", "units": 200, "revenue": 40000},
                    {"date": "2026-08-27", "units": 180, "revenue": 36000},
                ],
            }
        }
    
    def get_inventory_stock(self, item_code: str) -> Optional[Dict[str, Any]]:
        """Query stock levels for a specific item."""
        try:
            # Try real API first
            response = requests.get(
                f"{self.base_url}/inventory/stock",
                params={"item_code": item_code},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, requests.ConnectionError) as e:
            logger.warning(f"API call failed, using mock data: {e}")
            # Fallback to mock data
            if item_code in self.mock_data["inventory"]:
                return {
                    "item_code": item_code,
                    "data": self.mock_data["inventory"][item_code],
                    "source": "mock_data"
                }
            return {
                "error": f"Item '{item_code}' not found",
                "available_items": list(self.mock_data["inventory"].keys())
            }
    
    def recommend_vendors(self, item_code: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """Get vendor recommendations for an item."""
        try:
            response = requests.get(
                f"{self.base_url}/vendors/recommend",
                params={"item_code": item_code, "limit": limit},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, requests.ConnectionError) as e:
            logger.warning(f"API call failed, using mock data: {e}")
            if item_code in self.mock_data["vendors"]:
                vendors = self.mock_data["vendors"][item_code][:limit]
                return {
                    "item_code": item_code,
                    "vendors": vendors,
                    "source": "mock_data"
                }
            return {
                "error": f"No vendors found for item '{item_code}'",
                "available_items": list(self.mock_data["vendors"].keys())
            }
    
    def get_sales_data(self, item_code: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get sales data for an item."""
        try:
            response = requests.get(
                f"{self.base_url}/sales/history",
                params={"item_code": item_code, "days": days},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, requests.ConnectionError) as e:
            logger.warning(f"API call failed, using mock data: {e}")
            if item_code in self.mock_data["sales"]:
                sales = self.mock_data["sales"][item_code]
                return {
                    "item_code": item_code,
                    "sales_data": sales,
                    "source": "mock_data"
                }
            return {
                "error": f"No sales data found for item '{item_code}'",
                "available_items": list(self.mock_data["sales"].keys())
            }