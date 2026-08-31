from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from erp_helpdesk.agents.base_agent import BaseAgent
from erp_helpdesk.tools.erp_api_client import ERPAPIClient

from erp_helpdesk.config import config
import logging

logger = logging.getLogger(__name__)


@tool
def add_new_user(username: str, email: str) -> str:
    """Add a new user to the ERP system with the given username and email."""
    return f"Draft request created to add new user '{username}' with email '{email}'."


@tool
def give_permission_user(username: str, modulename: str) -> str:
    """Grant an existing ERP user permission/access to a specific module."""
    return f"Draft request created to grant '{username}' permission for module '{modulename}'."


@tool
def add_new_costcode(costcode_name: str, branch_name: str) -> str:
    """Create a new cost code under a specific branch."""
    return f"Draft request created to add new cost code '{costcode_name}' under branch '{branch_name}'."


@tool
def add_new_warehouse(warehouse_name: str, branch_name: str) -> str:
    """Create a new warehouse under a specific branch."""
    return f"Draft request created to add new warehouse '{warehouse_name}' under branch '{branch_name}'."


class ToolAgent(BaseAgent):
    """Agent 4: Categorizes a data change request, calls the matching tool, then creates a ticket."""

    TOOLS = [add_new_user, give_permission_user, add_new_costcode, add_new_warehouse]

    def __init__(self):
        super().__init__(model_name=config.tool_model, temperature=0.0)
        self._ticket_counter = 1000
        self.api_client = ERPAPIClient()
        self.llm_with_tools = self.llm.bind_tools(self.TOOLS)

    def _generate_ticket_id(self) -> str:
                    self._ticket_counter += 1
                    year = datetime.now().strftime("%Y")
                    return f"REQ-{year}-{self._ticket_counter:04d}"

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = input_data.get("original_message", "")
        user_id = input_data.get("user_id", "anonymous")
        image_data = input_data.get("image")

        logger.info(f"ToolAgent processing data change request from {user_id}")

        system_prompt = """You are a data request assistant for an ERP system.
        
        The user is requesting a data change in the ERP system. Based on their
        message, call the ONE tool that best matches their request:
        - add_new_user: for requests to add/create a new user
        - give_permission_user: for requests to grant a user permission/access to a module
        - add_new_costcode: for requests to add a new cost code
        - add_new_warehouse: for requests to add a new warehouse
        
        Extract the required arguments for the tool directly from the user's message.
        """

        response = self.llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        tool_calls = getattr(response, "tool_calls", None) or []
        tool_map = {t.name: t for t in self.TOOLS}

        if not tool_calls:
            logger.warning(f"No tool call matched for message: {user_message[:100]}")
            tool_name = None
            tool_args = {}
            summary = user_message[:100]
            ticket_details = user_message
        else:
            call = tool_calls[0]
            tool_name = call["name"]
            tool_args = call.get("args", {})

            selected_tool = tool_map.get(tool_name)
            tool_result = selected_tool.invoke(tool_args) if selected_tool else "Unknown tool selected."

            summary = f"{tool_name.replace('_', ' ').title()} - {tool_args}"
            ticket_details = tool_result

        
        ticket_id = self._generate_ticket_id()

        ticket = {
            "ticket_id": ticket_id,
            "summary": summary,
            "details": ticket_details,
            "reporter": user_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Open",
            "has_screenshot": image_data is not None,
        }

        return {
            "status": "success",
            "category": "DATA_CHANGE_REQUEST",
            "tool_called": tool_name,
            "tool_arguments": tool_args,
            "ticket": ticket,
            "user_id": user_id,
            "original_message": user_message
        }