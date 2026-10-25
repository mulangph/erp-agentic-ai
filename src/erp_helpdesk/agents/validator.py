import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from erp_helpdesk.agents.base_agent import BaseAgent
from erp_helpdesk.config import config
import logging

logger = logging.getLogger(__name__)

class Validator(BaseAgent):
    """Agent 5: Validator that formats responses and adds Devil's Advocate."""
    
    def __init__(self):
        super().__init__(model_name=config.validator_model, temperature=0.0)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        category = input_data.get("category", "UNKNOWN")
        user_message = input_data.get("original_message", "")
        user_id = input_data.get("user_id", "anonymous")
        
        logger.info(f"Validator processing {category} response for {user_id}")
        
        # Build the response based on category
        if category == "SUPPORT":
            answer = input_data.get("answer", "I couldn't find an answer.")
            rm_sample = input_data.get("rm_sample")
            sources = input_data.get("sources", [])
            
            final_message = f"**📚 Support Response:**\n\n{answer}"
            
            if rm_sample:
                final_message += f"\n\n**📝 Sample `.rm` File:**\n{rm_sample}"
            
            if sources:
                final_message += f"\n\n**📖 Sources:**\n" + "\n".join([f"- {s}" for s in sources])
            
            mitigations = [
                "Verify the steps match your ERP version",
                "Check that you have the required permissions",
                "Double-check any item codes or IDs before proceeding"
            ]
            
        elif category == "ERROR":
            ticket = input_data.get("ticket", {})
            screenshot_analysis = input_data.get("screenshot_analysis", {})
            
            # Build a nice ticket display. Lines must not be indented:
            # Markdown renders 4+ leading spaces as a code block.
            final_message = (
                "**🎫 Ticket Created Successfully!**\n\n"
                "Here are your ticket details:\n\n"
                "| Field | Value |\n"
                "|-------|-------|\n"
                f"| **Ticket ID** | `{ticket.get('ticket_id', 'N/A')}` |\n"
                f"| **Summary** | {ticket.get('summary', 'No summary')} |\n"
                f"| **Severity** | {ticket.get('severity', 'N/A')}/5 |\n"
                f"| **Status** | {ticket.get('status', 'Open')} |\n"
                f"| **Reporter** | {ticket.get('reporter', 'N/A')} |\n"
                f"| **Created** | {ticket.get('created_at', 'N/A')} |\n"
                f"| **Has Screenshot** | {'✅ Yes' if ticket.get('has_screenshot') else '❌ No'} |\n\n"
                "**📝 Details:**\n\n"
                f"{ticket.get('details', user_message)}\n\n"
            )

            # Add screenshot analysis if available
            if screenshot_analysis:
                final_message += "**📷 Screenshot Analysis:**\n\n"

                if screenshot_analysis.get('suggested_issue'):
                    final_message += f"- **Suggested Issue:** {screenshot_analysis['suggested_issue']}\n"
                if screenshot_analysis.get('potential_root_cause'):
                    final_message += f"- **Potential Root Cause:** {screenshot_analysis['potential_root_cause']}\n"
                if screenshot_analysis.get('error_code'):
                    final_message += f"- **Error Code:** {screenshot_analysis['error_code']}\n"
                if screenshot_analysis.get('error_message'):
                    final_message += f"- **Error Message:** {screenshot_analysis['error_message']}\n"
                if screenshot_analysis.get('module'):
                    final_message += f"- **Module:** {screenshot_analysis['module']}\n"
                if screenshot_analysis.get('user_action'):
                    final_message += f"- **User Action:** {screenshot_analysis['user_action']}\n"
                if screenshot_analysis.get('additional_details'):
                    final_message += f"- **Additional Details:** {screenshot_analysis['additional_details']}\n"
                final_message += "\n"

            final_message += (
                "**📌 Next Steps:**\n"
                "1. A support agent will review your ticket\n"
                "2. You'll receive updates via email\n"
                "3. Check ticket status at any time using the ticket ID\n"
            )
            
            mitigations = [
                "Make sure to include any additional error messages you see",
                "Double-check that you have the necessary permissions",
                "Try reproducing the issue to confirm it's consistent"
            ]
            
        elif category == "DATA_CHANGE_REQUEST":
            ticket = input_data.get("ticket", {})
            tool_called = input_data.get("tool_called")
            tool_arguments = input_data.get("tool_arguments", {})
            
            # Build a nice ticket display (no indentation, see ERROR above)
            final_message = (
                "**🎫 Data Change Request Submitted!**\n\n"
                "Here are your ticket details:\n\n"
                "| Field | Value |\n"
                "|-------|-------|\n"
                f"| **Ticket ID** | `{ticket.get('ticket_id', 'N/A')}` |\n"
                f"| **Summary** | {ticket.get('summary', 'No summary')} |\n"
                f"| **Status** | {ticket.get('status', 'Open')} |\n"
                f"| **Reporter** | {ticket.get('reporter', 'N/A')} |\n"
                f"| **Created** | {ticket.get('created_at', 'N/A')} |\n"
                f"| **Has Screenshot** | {'✅ Yes' if ticket.get('has_screenshot') else '❌ No'} |\n\n"
                "**📝 Details:**\n\n"
                f"{ticket.get('details', user_message)}\n\n"
            )

            # Show which tool was identified and called for this request
            if tool_called:
                final_message += (
                    "**🛠️ Action Identified:**\n\n"
                    f"- **Tool Called:** `{tool_called}`\n"
                    f"- **Arguments:** {tool_arguments}\n\n"
                )

            final_message += (
                "**📌 Next Steps:**\n"
                "1. Your request will be reviewed and applied to the ERP system\n"
                "2. You'll receive updates via email\n"
                "3. Check ticket status at any time using the ticket ID\n"
            )
            
            mitigations = [
                "Double-check the details you provided are correct",
                "Verify you have authorization to request this change",
                "Confirm the ticket ID for tracking your request"
            ]
            
        else:
            final_message = "I processed your request but found an unknown category. Please try rephrasing."
            mitigations = ["Please provide more context", "Try being more specific"]
        
        return {
            "status": "success",
            "final_message": final_message,
            "mitigations": mitigations,
            "is_correct": True,
            "changes_made": "None",
            "user_id": user_id
        }