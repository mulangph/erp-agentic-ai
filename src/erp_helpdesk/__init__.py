"""
ERP Helpdesk Agentic AI - Multi-modal Intelligent Helpdesk System

A production-ready agentic AI system for ERP helpdesk automation with:
- Multi-modal support (text + images)
- RAG-powered support answers
- Automated ticket creation
- Data query capabilities
- Self-validation with Devil's Advocate double-check
"""

__version__ = "1.0.0"
__author__ = "Your Team"
__description__ = "Agentic AI Helpdesk for ERP Systems"

# Import key components for easy access
from erp_helpdesk.config import config
from main import main

# Import agents (these come from the agents/__init__.py)
from erp_helpdesk.agents import (
    RouterAgent,
    RAGAgent,
    TicketAgent,
    ToolAgent,
    Validator,
)

# Import utilities
from erp_helpdesk.utils.image_processor import ImageProcessor

# Import tools
from erp_helpdesk.tools.erp_api_client import ERPAPIClient

# Define what's available when someone does: from erp_helpdesk import *
__all__ = [
    # Core
    "config",
    "main",
    
    # Agents
    "RouterAgent",
    "RAGAgent",
    "TicketAgent",
    "ToolAgent",
    "Validator",
    
    # Utilities
    "ImageProcessor",
    "ERPAPIClient",
    
    # Metadata
    "__version__",
    "__author__",
]

# Optional: Package-level initialization
def setup():
    """Initialize the ERP Helpdesk package."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"ERP Helpdesk v{__version__} initialized")
    
    # Check if config is properly set up
    if not config.openai_api_key:
        logger.warning("OpenAI API key not found in environment variables!")
        logger.warning("Please set OPENAI_API_KEY in your .env file")
    
    return True

# Run setup when package is imported
setup()