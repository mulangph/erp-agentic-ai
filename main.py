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
        
        # Add the validator's points to double-check
        mitigations = final_result.get("mitigations", [])
        mitigations_text = ""
        if mitigations:
            mitigations_text = "\n\n---\n**Before you act, check:**\n" + "\n".join(
                f"- {m}" for m in mitigations
            )

        return final_result["final_message"] + mitigations_text
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return f"❌ I encountered an error: {str(e)}"

# ═══════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════

EXAMPLES_DIR = os.path.join(ROOT_DIR, "test_data", "image")

THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.blue,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("IBM Plex Sans"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "ui-monospace", "monospace"],
    radius_size=gr.themes.sizes.radius_md,
).set(
    body_background_fill="#F4F6F5",
    body_text_color="#1C2530",
    block_background_fill="#FFFFFF",
    block_border_color="#DCE1E4",
    block_border_width="1px",
    block_shadow="none",
    block_label_background_fill="#FFFFFF",
    button_primary_background_fill="#1E4E79",
    button_primary_background_fill_hover="#173D5F",
    button_primary_text_color="#FFFFFF",
    button_secondary_background_fill="#FFFFFF",
    button_secondary_background_fill_hover="#EEF1F3",
    button_secondary_border_color="#C9D0D5",
    button_secondary_text_color="#1C2530",
    color_accent="#1E4E79",
    color_accent_soft="#E3ECF4",
    input_background_fill="#FFFFFF",
    input_border_color="#C9D0D5",
    input_border_color_focus="#1E4E79",
    # Dark mode equivalents
    body_background_fill_dark="#0F151B",
    body_text_color_dark="#E6EBEF",
    block_background_fill_dark="#18212B",
    block_border_color_dark="#2C3844",
    block_label_background_fill_dark="#18212B",
    button_primary_background_fill_dark="#2F6EA5",
    button_primary_background_fill_hover_dark="#3A7DB8",
    button_secondary_background_fill_dark="#18212B",
    button_secondary_background_fill_hover_dark="#223040",
    button_secondary_border_color_dark="#3A4754",
    button_secondary_text_color_dark="#E6EBEF",
    input_background_fill_dark="#121A22",
    input_border_color_dark="#3A4754",
    input_border_color_focus_dark="#7FB3E0",
)

CSS = """
/* Colour tokens: light values here, dark values under .dark */
:root {
  --hd-ink: #1C2530;          /* headings */
  --hd-body: #3C4752;         /* body text */
  --hd-muted: #5B6773;        /* secondary text */
  --hd-surface: #FFFFFF;      /* cards */
  --hd-border: #DCE1E4;
  --hd-control-border: #C9D0D5;
  --hd-accent: #1E4E79;
  --cap-support: #1E4E79;
  --cap-error: #D99A00;
  --cap-change: #2F7D5B;
}
.dark {
  --hd-ink: #E6EBEF;
  --hd-body: #C9D2D9;
  --hd-muted: #9AA7B2;
  --hd-surface: #18212B;
  --hd-border: #2C3844;
  --hd-control-border: #3A4754;
  --hd-accent: #7FB3E0;
  --cap-support: #5C9BD1;
  --cap-error: #F2B632;
  --cap-change: #4FB287;
}

.gradio-container { max-width: 1240px !important; margin: 0 auto !important; padding: 28px 24px 16px !important; }
footer { display: none !important; }

/* Header */
#app-header { margin-bottom: 18px; }
#app-header h1 { font-size: 26px; font-weight: 600; letter-spacing: -0.01em; margin: 0 0 4px; color: var(--hd-ink); }
#app-header p { font-size: 15px; color: var(--hd-muted); margin: 0; max-width: 70ch; }

/* Main row: both columns start at the same top edge */
#main-row { align-items: stretch; gap: 20px; }

/* Chat column */
#chat-col { gap: 10px; }
#chatbot { border-radius: 10px; }
#chatbot hr { margin: 10px 0 !important; }
#chatbot .placeholder-content, #chatbot .placeholder { color: var(--hd-muted); }
#composer { border-radius: 10px; }
#composer textarea { font-size: 15px; }

/* Sidebar */
#side-col { gap: 14px; }
.side-card { background: var(--hd-surface); border: 1px solid var(--hd-border); border-radius: 10px; padding: 16px 18px; }
.side-card h3 { font-size: 14px; font-weight: 600; color: var(--hd-ink); margin: 0 0 12px; }
.capability { border-left: 3px solid var(--cap); padding: 2px 0 2px 12px; margin-bottom: 14px; }
.capability:last-child { margin-bottom: 0; }
.capability strong { display: block; font-size: 14px; font-weight: 600; color: var(--hd-ink); }
.capability span { display: block; font-size: 13px; color: var(--hd-muted); line-height: 1.45; margin-top: 2px; }
.cap-support { --cap: var(--cap-support); }
.cap-error   { --cap: var(--cap-error); }
.cap-change  { --cap: var(--cap-change); }
.checks { margin: 0; padding-left: 18px; list-style: disc; font-size: 13px; color: var(--hd-body); line-height: 1.6; }
#session-box { border-radius: 10px; }
#clear-btn { width: 100%; border: 1px solid var(--hd-control-border); font-weight: 500; font-size: 14px; }
#side-col > * { margin: 0 !important; }

/* Strip Gradio's wrapper chrome from raw HTML blocks */
.bare { padding: 0 !important; border: none !important; background: transparent !important; box-shadow: none !important; }

/* Suggestions: one tidy row under the composer */
#suggestions { gap: 8px; flex-wrap: wrap; }
#suggestions .suggestion { flex: 0 0 auto !important; min-width: 0 !important; width: auto !important;
  font-weight: 400; font-size: 13px; color: var(--hd-body); border-radius: 999px; padding: 6px 14px; }
#suggestions .suggestion:hover { border-color: var(--hd-accent); color: var(--hd-accent); }

/* Stack the columns on narrow screens */
@media (max-width: 860px) {
  .gradio-container { padding: 16px 12px 12px !important; }
  #main-row { flex-direction: column; }
  #side-col { min-width: 100% !important; }
}
"""

HEADER_HTML = """
<div id="app-header">
  <h1>ERP Helpdesk</h1>
  <p>Ask how to do something in the ERP, report an error with a screenshot, or request a change such as new user access.</p>
</div>
"""

CAPABILITIES_HTML = """
<div class="side-card">
  <h3>What I can help with</h3>
  <div class="capability cap-support">
    <strong>How-to questions</strong>
    <span>Step-by-step answers from the ERP guides, with sources.</span>
  </div>
  <div class="capability cap-error">
    <strong>Error reports</strong>
    <span>Attach a screenshot and I'll open a ticket with a severity rating.</span>
  </div>
  <div class="capability cap-change">
    <strong>Change requests</strong>
    <span>New users, module access, cost codes and warehouses, drafted for approval.</span>
  </div>
</div>
"""

CHECKS_HTML = """
<div class="side-card">
  <h3>How replies are checked</h3>
  <ul class="checks">
    <li>Each request goes to a specialist agent</li>
    <li>A validator reviews every reply</li>
    <li>Points to double-check are listed at the end</li>
    <li>Changes are drafted, never applied automatically</li>
  </ul>
</div>
"""

EMPTY_STATE = (
    "**How can I help today?**\n\n"
    "Describe your question or problem below. "
    "Use the paperclip to attach a screenshot of an error."
)


SAMPLE_SCREENSHOT = os.path.join(EXAMPLES_DIR, "Odoo_error.png")

# (button label, composer value)
SUGGESTIONS = [
    ("How do I create a purchase order?",
     {"text": "How do I create a purchase order?", "files": []}),
    ("Report a sample invoice error",
     {"text": "I got this error when saving an invoice",
      "files": [SAMPLE_SCREENSHOT] if os.path.exists(SAMPLE_SCREENSHOT) else []}),
    ("Give jsmith Inventory access",
     {"text": "Give user jsmith access to the Inventory module", "files": []}),
]


def create_ui():
    with gr.Blocks(title="ERP Helpdesk", theme=THEME, css=CSS) as demo:
        pending = gr.State(None)

        gr.HTML(HEADER_HTML, elem_classes="bare", padding=False)

        with gr.Row(elem_id="main-row", equal_height=False):
            # ── Conversation ─────────────────────────────────
            with gr.Column(scale=3, elem_id="chat-col"):
                chatbot = gr.Chatbot(
                    elem_id="chatbot",
                    type="messages",
                    height=600,
                    show_label=False,
                    placeholder=EMPTY_STATE,
                    show_copy_button=True,
                )
                composer = gr.MultimodalTextbox(
                    elem_id="composer",
                    show_label=False,
                    placeholder="Ask a question or describe an error…",
                    file_types=["image"],
                    file_count="single",
                    sources=["upload"],
                    submit_btn=True,
                    autofocus=True,
                )
                with gr.Row(elem_id="suggestions"):
                    suggestion_btns = [
                        gr.Button(label, size="sm", variant="secondary", elem_classes="suggestion")
                        for label, _ in SUGGESTIONS
                    ]

            # ── Sidebar ──────────────────────────────────────
            with gr.Column(scale=1, min_width=280, elem_id="side-col"):
                gr.HTML(CAPABILITIES_HTML, elem_classes="bare", padding=False)
                gr.HTML(CHECKS_HTML, elem_classes="bare", padding=False)
                with gr.Group(elem_id="session-box"):
                    user_id_input = gr.Textbox(
                        label="User ID",
                        value="user_001",
                        max_lines=1,
                    )
                clear_btn = gr.Button("Clear conversation", variant="secondary", size="sm", elem_id="clear-btn")

        # ── Events ───────────────────────────────────────────
        def add_user_turn(message, history):
            """Show the user's message straight away and lock the composer."""
            history = history or []
            text = (message or {}).get("text", "").strip()
            files = (message or {}).get("files", [])

            if not text and not files:
                return history, gr.MultimodalTextbox(value=None), None

            if files:
                history.append({"role": "user", "content": {"path": files[0]}})
            if text:
                history.append({"role": "user", "content": text})

            return history, gr.MultimodalTextbox(value=None, interactive=False), {"text": text, "files": files}

        def bot_turn(message, history, user_id):
            """Run the agents and append the reply."""
            if message is None:
                return history, gr.MultimodalTextbox(interactive=True)

            image_bytes = None
            if message["files"]:
                with open(message["files"][0], "rb") as f:
                    image_bytes = f.read()

            reply = process_message_with_image(message["text"], image_bytes, user_id or "anonymous")
            history.append({"role": "assistant", "content": reply})
            return history, gr.MultimodalTextbox(interactive=True)

        composer.submit(
            add_user_turn,
            inputs=[composer, chatbot],
            outputs=[chatbot, composer, pending],
        ).then(
            bot_turn,
            inputs=[pending, chatbot, user_id_input],
            outputs=[chatbot, composer],
        )

        for btn, (_, value) in zip(suggestion_btns, SUGGESTIONS):
            btn.click(lambda v=value: gr.MultimodalTextbox(value=v), outputs=[composer])

        def clear_conversation(user_id):
            sessions.pop(user_id, None)
            return [], gr.MultimodalTextbox(value=None, interactive=True), None

        clear_btn.click(
            clear_conversation,
            inputs=[user_id_input],
            outputs=[chatbot, composer, pending],
        )

    return demo

def main():
    demo = create_ui()
    port = int(os.getenv("PORT", "7860"))
    logger.info(f"🚀 Starting Gradio UI on http://localhost:{port}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )

if __name__ == "__main__":
    main()