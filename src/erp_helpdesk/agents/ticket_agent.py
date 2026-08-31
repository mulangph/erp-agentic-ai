import json
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from erp_helpdesk.agents.base_agent import BaseAgent
from erp_helpdesk.config import config
import logging

logger = logging.getLogger(__name__)

class TicketAgent(BaseAgent):
    """Agent 3: Ticket creator with image attachment support."""
    
    def __init__(self):
        super().__init__(model_name=config.ticket_model, temperature=0.0)
        self._ticket_counter = 1000
        self.vision_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0
        )
        
    def _generate_ticket_id(self) -> str:
        self._ticket_counter += 1
        year = datetime.now().strftime("%Y")
        return f"ERP-{year}-{self._ticket_counter:04d}"
    
    def _determine_severity(self, message: str, screenshot_analysis: Dict = None) -> int:
        """Enhanced severity detection with visual context."""
        severity_keywords = {
            1: ["crash", "down", "not working", "error", "failed", "critical", "urgent", "emergency"],
            2: ["broken", "issue", "problem", "wrong", "incorrect"],
            3: ["slow", "delay", "stuck", "timeout"],
            4: ["question", "how to", "where", "guide"],
            5: ["suggestion", "request", "feature", "enhancement"],
        }
        
        combined_text = message.lower()
        
        # Add screenshot analysis text if available
        if screenshot_analysis:
            if screenshot_analysis.get("suggested_issue"):
                combined_text += " " + screenshot_analysis["suggested_issue"].lower()
            if screenshot_analysis.get("error_message"):
                combined_text += " " + screenshot_analysis["error_message"].lower()
            if screenshot_analysis.get("error_code"):
                combined_text += " " + screenshot_analysis["error_code"].lower()
        
        for severity, keywords in severity_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return severity
        
        # Check for visual indicators of severity
        if screenshot_analysis:
            if screenshot_analysis.get("error_code") or screenshot_analysis.get("error_message"):
                return 2
            if "error" in str(screenshot_analysis).lower() or "failed" in str(screenshot_analysis).lower():
                return 2
        
        return 3
    
    def _analyze_screenshot_for_ticket(self, image_data: Dict) -> Dict:
        """Extract error information from screenshot with suggested issue."""
        if not image_data or not image_data.get("base64"):
            return {}
            
        try:
            prompt = """You are an expert ERP system analyst. Analyze this screenshot and provide a detailed ticket analysis.

            Extract the following information:
            
            1. Error code or number (if visible)
            2. Error message or description (if visible)
            3. What module/screen shows the error
            4. What the user was likely trying to do
            5. SUGGESTED ISSUE: Write a clear, concise description of what you think went wrong (this will be used as the ticket summary)
            6. POTENTIAL ROOT CAUSE: What might be causing this issue
            
            Output as JSON:
            {
                "error_code": "string or null",
                "error_message": "string or null",
                "module": "string or null",
                "user_action": "What the user was trying to do",
                "suggested_issue": "Clear description of the issue",
                "potential_root_cause": "What might be causing this",
                "additional_details": "Any other important observations"
            }
            
            IMPORTANT: Return ONLY the JSON object, no other text.
            """
            
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_data['base64']}"}
                }
            ]
            
            response = self.vision_llm.invoke([HumanMessage(content=content)])
            
            try:
                result = json.loads(response.content)
                logger.info(f"✅ Screenshot analysis successful: {result}")
                return result
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse screenshot analysis JSON: {response.content[:200]}")
                # Try to extract information from the text response
                text = response.content
                return {
                    "error_code": None,
                    "error_message": None,
                    "module": None,
                    "user_action": None,
                    "suggested_issue": "Issue detected in screenshot - please review manually",
                    "potential_root_cause": "Unable to determine from screenshot",
                    "additional_details": text[:500] if text else None
                }
            
        except Exception as e:
            logger.error(f"Error analyzing screenshot for ticket: {e}")
            return {
                "error_code": None,
                "error_message": None,
                "module": None,
                "user_action": None,
                "suggested_issue": "Unable to analyze screenshot",
                "potential_root_cause": "Screenshot analysis failed",
                "additional_details": str(e)
            }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = input_data.get("original_message", "")
        user_id = input_data.get("user_id", "anonymous")
        image_data = input_data.get("image")
        image_context = input_data.get("image_context", "")
        
        logger.info(f"TicketAgent creating ticket for {user_id}")
        logger.info(f"User message: {user_message}")
        logger.info(f"Has image: {image_data is not None}")
        
        # Analyze screenshot for error details
        screenshot_analysis = {}
        if image_data:
            screenshot_analysis = self._analyze_screenshot_for_ticket(image_data)
            logger.info(f"Screenshot analysis result: {json.dumps(screenshot_analysis, indent=2)}")
        
        # Generate summary - use suggested issue if available
        if screenshot_analysis.get("suggested_issue") and screenshot_analysis["suggested_issue"] != "Unable to analyze screenshot":
            summary = screenshot_analysis["suggested_issue"]
            logger.info(f"Using suggested issue as summary: {summary}")
        else:
            # Generate summary using LLM
            summary_prompt = f"""Generate a brief, 5-7 word summary of this error report. Be specific and descriptive.

            User reported: {user_message}
            
            {f"Screenshot shows: {screenshot_analysis.get('additional_details', '')}" if screenshot_analysis else ""}
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a ticket summarization expert. Create concise ticket summaries."),
                HumanMessage(content=summary_prompt)
            ])
            summary = response.content.strip()
            logger.info(f"Generated summary: {summary}")
        
        # Determine severity with visual context
        severity = self._determine_severity(user_message, screenshot_analysis)
        logger.info(f"Determined severity: {severity}")
        
        # Build detailed ticket description
        details_parts = [user_message]
        
        # Add screenshot analysis to ticket details
        if screenshot_analysis:
            details_parts.append("\n\n--- 📷 SCREENSHOT ANALYSIS ---")
            
            if screenshot_analysis.get("suggested_issue"):
                details_parts.append(f"📋 Suggested Issue: {screenshot_analysis['suggested_issue']}")
            
            if screenshot_analysis.get("potential_root_cause"):
                details_parts.append(f"🔍 Potential Root Cause: {screenshot_analysis['potential_root_cause']}")
            
            if screenshot_analysis.get("error_code"):
                details_parts.append(f"❌ Error Code: {screenshot_analysis['error_code']}")
            
            if screenshot_analysis.get("error_message"):
                details_parts.append(f"📝 Error Message: {screenshot_analysis['error_message']}")
            
            if screenshot_analysis.get("module"):
                details_parts.append(f"🖥️ Module: {screenshot_analysis['module']}")
            
            if screenshot_analysis.get("user_action"):
                details_parts.append(f"👤 User Action: {screenshot_analysis['user_action']}")
            
            if screenshot_analysis.get("additional_details"):
                details_parts.append(f"📌 Additional Details: {screenshot_analysis['additional_details']}")
        
        if image_context:
            details_parts.append(f"\n🖼️ Image Context: {image_context}")
        
        ticket_details = "\n".join(details_parts)
        
        # Generate ticket ID
        ticket_id = self._generate_ticket_id()
        
        # Build ticket
        ticket = {
            "ticket_id": ticket_id,
            "summary": summary,
            "details": ticket_details,
            "reporter": user_id,
            "severity": severity,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Open",
            "has_screenshot": image_data is not None,
        }
        
        # Store screenshot analysis in ticket for validator to use
        if image_data and screenshot_analysis:
            ticket["screenshot_analysis"] = screenshot_analysis
            ticket["screenshot_type"] = image_data.get("type", "unknown")
        
        # Include OCR text if available
        if image_data and image_data.get("ocr_text"):
            ticket["ocr_extracted_text"] = image_data["ocr_text"][:500]
        
        logger.info(f"✅ Ticket created: {ticket['ticket_id']}")
        logger.info(f"📋 Summary: {summary}")
        logger.info(f"📝 Details preview: {ticket_details[:200]}...")
        
        return {
            "status": "success",
            "category": "ERROR",
            "ticket": ticket,
            "user_id": user_id,
            "original_message": user_message,
            "image": image_data,
            "screenshot_analysis": screenshot_analysis
        }