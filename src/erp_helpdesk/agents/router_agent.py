import json
from typing import Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from erp_helpdesk.agents.base_agent import BaseAgent
from erp_helpdesk.config import config
import logging

logger = logging.getLogger(__name__)

class RouterAgent(BaseAgent):
    """Agent 1: Multi-modal router that can analyze images."""
    
    def __init__(self):
        super().__init__(model_name=config.router_model, temperature=0.0)
        # Vision model for image analysis
        self.vision_llm = ChatOpenAI(
            model="gpt-4o",  # Vision requires gpt-4o
            temperature=0.0,
            max_tokens=500
        )
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = input_data.get("message", "")
        user_id = input_data.get("user_id", "anonymous")
        image_data = input_data.get("image")
        
        logger.info(f"Routing message from {user_id}: {user_message[:50] if user_message else '[No text]'}...")
        
        # Analyze image if present
        image_analysis = None
        if image_data:
            image_analysis = self._analyze_image(image_data)
            logger.info(f"Image analysis: {image_analysis[:200] if image_analysis else 'None'}")
        
        system_prompt = """You are a precise classifier for an ERP helpdesk.
        
        Classify the user's message into EXACTLY ONE of these categories:
        
        1. SUPPORT - Questions about how to use the ERP system (how-to's, where-to's)
        2. ERROR - Reports of system failures, bugs, or error messages
        3. DATA_CHANGE_REQUEST - Requests to add, create, update, or grant something in the ERP (e.g. adding a user, granting permissions, creating a cost code, creating a warehouse)
        
        Rules:
        - If an image is provided, consider it as context for the classification
        - Error screenshots strongly suggest ERROR category
        - UI screenshots with questions suggest SUPPORT category
        - If the user is asking to add, create, update, or grant something (a request), classify it as DATA_CHANGE_REQUEST
        - If you're unsure, set confidence to 0.5 and ask clarification.
        - Output must be valid JSON.
        
        Output format:
        {
            "category": "SUPPORT|ERROR|DATA_CHANGE_REQUEST",
            "confidence": 0.95,
            "clarification_question": null or "Your clarifying question here...",
            "image_context": "Brief description of what the image shows"
        }
        
        IMPORTANT: Return ONLY the JSON object, no other text.
        """
        
        # Build message content
        content = f"User Message: {user_message}\n\nImage Analysis (if available): {image_analysis or 'No image provided'}"
        
        def _classify():
            response = self.vision_llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=content)
            ])
            # Simple JSON parsing with fallback
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                # If JSON parsing fails, return a default
                logger.warning(f"Failed to parse JSON, using default. Response: {response.content[:200]}")
                return {
                    "category": "SUPPORT",
                    "confidence": 0.5,
                    "clarification_question": "I had trouble understanding. Could you rephrase?",
                    "image_context": None
                }
        
        result = _classify()
        
        # Ensure required fields exist
        if "category" not in result:
            result["category"] = "SUPPORT"
            result["confidence"] = 0.5
        
        # Add image context to result
        result["image_analysis"] = image_analysis
        result["has_image"] = image_data is not None
        
        # If confidence is low, return clarification
        if result.get("confidence", 0) < 0.85 and result.get("clarification_question"):
            return {
                "status": "needs_clarification",
                "category": result.get("category"),
                "question": result["clarification_question"],
                "original_message": user_message,
                "user_id": user_id,
                "image": image_data
            }
        
        return {
            "status": "success",
            "category": result["category"],
            "confidence": result["confidence"],
            "original_message": user_message,
            "user_id": user_id,
            "image": image_data,
            "image_context": result.get("image_context"),
            "image_analysis": image_analysis
        }
    
    def _analyze_image(self, image_data: Dict[str, Any]) -> str:
        """Analyze image content using vision model."""
        try:
            vision_prompt = """Analyze this image and describe what you see in the context of an ERP system.
            
            Specifically note:
            1. Is this an error message or dialog? If so, what error code?
            2. Is this a UI element? What screen/module?
            3. What is the user likely trying to do based on this image?
            
            Keep description concise (max 100 words).
            """
            
            response = self.vision_llm.invoke([
                HumanMessage(content=[
                    {"type": "text", "text": vision_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data['base64']}"}}
                ])
            ])
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Image analysis failed: {str(e)}"