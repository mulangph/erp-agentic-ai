"""
ERP Helpdesk Agentic AI - Main Entry Point
This file is located in the root directory for easy execution.
"""

import sys
import os
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════
# Setup paths - add src directory to Python path
# ═══════════════════════════════════════════════════════════
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, 'src')

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Load environment variables
load_dotenv(os.path.join(ROOT_DIR, '.env'))
# ═══════════════════════════════════════════════════════════

import gradio as gr
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime
from PIL import Image
import io

# Now import from the package
from erp_helpdesk.config import config
from erp_helpdesk.agents.router_agent import RouterAgent
from erp_helpdesk.agents.rag_agent import RAGAgent
from erp_helpdesk.agents.ticket_agent import TicketAgent
from erp_helpdesk.agents.tool_agent import ToolAgent
from erp_helpdesk.agents.validator import Validator
from erp_helpdesk.utils.image_processor import ImageProcessor

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"🚀 Starting ERP Helpdesk Agentic AI v1.0.0")
logger.info(f"📁 Root directory: {ROOT_DIR}")
logger.info(f"📁 Source directory: {SRC_DIR}")

# Initialize all agents
logger.info("Initializing agents...")
router_agent = RouterAgent()
rag_agent = RAGAgent()
ticket_agent = TicketAgent()
data_seer = ToolAgent()
validator = Validator()
logger.info("✅ All agents initialized successfully")

# Session storage
sessions = {}

def get_or_create_session(user_id: str) -> Dict[str, Any]:
    if user_id not in sessions:
        sessions[user_id] = {
            "conversation_history": [],
            "ticket_count": 0,
            "last_images": []
        }
    return sessions[user_id]

def process_message_with_image(
    message: str, 
    image: Optional[gr.File], 
    user_id: str = "anonymous"
) -> str:
    """Main orchestration function with image support."""
    logger.info(f"Processing message from {user_id}: {message[:50] if message else '[No text]'}...")
    
    # Process image if provided
    image_data = None
    
    if image is not None:
        try:
            # Read image bytes
            if hasattr(image, 'read'):
                image_bytes = image.read()
            else:
                image_bytes = image
            
            # Resize if needed
            image_bytes = ImageProcessor.resize_image_if_needed(image_bytes)
            
            # Encode for API
            image_base64 = ImageProcessor.encode_image_to_base64(image_bytes)
            
            # Detect image type
            image_type = ImageProcessor.detect_image_type(image_bytes)
            logger.info(f"Detected image type: {image_type}")
            
            # Try OCR
            ocr_text = ImageProcessor.extract_text_from_image(image_bytes)
            
            # Store in session
            session = get_or_create_session(user_id)
            session["last_images"].append({
                "timestamp": datetime.now().isoformat(),
                "type": image_type,
                "ocr_text": ocr_text
            })
            session["last_images"] = session["last_images"][-5:]
            
            image_data = {
                "bytes": image_bytes,
                "base64": image_base64,
                "type": image_type,
                "ocr_text": ocr_text,
                "description": f"OCR extracted text: {ocr_text}" if ocr_text else None
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return f"❌ Error processing image: {str(e)}"
    
    # Update session
    session = get_or_create_session(user_id)
    session["conversation_history"].append({
        "role": "user", 
        "content": message,
        "has_image": image_data is not None
    })
    
    try:
        # Step 1: Route the message
        routing_input = {
            "message": message,
            "user_id": user_id,
            "image": image_data
        }
        
        routing_result = router_agent.process(routing_input)
        
        if routing_result.get("status") == "needs_clarification":
            return f"🤔 {routing_result['question']}"
        
        category = routing_result.get("category")
        logger.info(f"Message categorized as: {category}")
        
        # Step 2: Route to appropriate agent
        agent_input = {
            **routing_result,
            "image": image_data
        }
        
        if category == "SUPPORT":
            agent_result = rag_agent.process(agent_input)
        elif category == "ERROR":
            agent_result = ticket_agent.process(agent_input)
        elif category == "DATA_CHANGE_REQUEST":
            agent_result = data_seer.process(agent_input)
        else:
            return "I couldn't understand your request. Please try again with more detail."
        
        # Step 3: Validate with Devil's Advocate
        final_result = validator.process({
            **agent_result,
            "image": image_data
        })
        
        # Store in session
        session["conversation_history"].append({
            "role": "assistant",
            "content": final_result["final_message"]
        })
        
        # Add mitigations
        mitigations_text = "\n\n---\n\n" + "\n".join([
            f"🔍 **Concern:** {m}" for m in final_result.get("mitigations", [])
        ])
        
        return final_result["final_message"] + mitigations_text
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return f"❌ I encountered an error: {str(e)}"

def create_ui():
    # ✅ FIX: Use the new chatbot format with type='messages'
    with gr.Blocks(title="ERP Helpdesk Agentic AI") as demo:
        gr.Markdown("""
        # 🏢 ERP Helpdesk Agentic AI
        
        **I can help with:**
        - 📚 **Support:** How-to questions and ERP guidance
        - 🐛 **Error Reports:** File tickets for system issues (upload screenshots!)
        - 📊 **Data Change Request:** Add permission to users, create new cost codes, create new warehouse.
        
        **📷 NEW:** Upload screenshots of errors or UI issues for better assistance!
        
        *Every response includes a "Devil's Advocate" double-check for reliability.*
        """)
        
        with gr.Row():
            with gr.Column(scale=4):
                # ✅ FIX: Use type='messages' for the new format
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    type='messages'  # Use openai-style dict format
                )
            with gr.Column(scale=1):
                gr.Markdown("### 🛡️ Trust Features")
                gr.Markdown("- ✅ Response validated by Agent 5")
                gr.Markdown("- 🔍 Double-Check (Devil's Advocate)")
                gr.Markdown("- 💰 Cost-budgeted (max $0.10/request)")
                gr.Markdown("- ⏱️ Timeout: 30 seconds")
                gr.Markdown("- 📷 **Vision-enabled**")
                
                gr.Markdown("### 📊 Session Info")
                user_id_input = gr.Textbox(
                    label="User ID",
                    value="user_001",
                    visible=True
                )
        
        with gr.Row():
            with gr.Column(scale=8):
                msg_input = gr.Textbox(
                    label="Type your message...",
                    placeholder="e.g., 'How do I add a purchase order line?' or 'Check stock for item Cement'",
                    lines=2
                )
            with gr.Column(scale=2):
                image_input = gr.File(
                    label="📷 Upload Screenshot",
                    file_types=[".png", ".jpg", ".jpeg", ".gif", ".bmp"],
                    type="binary"
                )
        
        with gr.Row():
            send_btn = gr.Button("Send", variant="primary", scale=1)
            clear_image = gr.Button("Clear Image", variant="secondary", scale=1)
        
        # ✅ FIX: Use list of messages with role/content format
        state = gr.State([])
        
        def clear_image_input():
            return None
        
        clear_image.click(clear_image_input, outputs=[image_input])
        
        def respond(message, image, history, user_id):
            if not message.strip() and image is None:
                # ✅ FIX: Use messages format
                history.append({"role": "assistant", "content": "⚠️ Please provide a message or screenshot"})
                return history, "", None
            
            # Add user message
            user_content = message if message else "[Image uploaded]"
            history.append({"role": "user", "content": user_content})
            
            # Get response
            response = process_message_with_image(message, image, user_id)
            
            # Add assistant message
            history.append({"role": "assistant", "content": response})
            return history, "", None
        
        send_btn.click(
            respond,
            inputs=[msg_input, image_input, state, user_id_input],
            outputs=[chatbot, msg_input, image_input]
        )
        
        msg_input.submit(
            respond,
            inputs=[msg_input, image_input, state, user_id_input],
            outputs=[chatbot, msg_input, image_input]
        )
        
        # ✅ FIX: Clear button using a function instead of ClearButton
        def clear_history():
            return [], "", None
        
        clear_btn = gr.Button("Clear Conversation", variant="secondary")
        clear_btn.click(
            clear_history,
            inputs=[],
            outputs=[chatbot, msg_input, image_input]
        )
    
    return demo

def main():
    demo = create_ui()
    logger.info("🚀 Starting Gradio UI on http://localhost:7860")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

if __name__ == "__main__":
    main()