import os
from dotenv import load_dotenv

load_dotenv()

# Project root (two levels above src/erp_helpdesk/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Config:
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Model Mapping - Use simpler models
    router_model: str = "gpt-4o-mini"  # Cheaper and faster
    rag_model: str = "gpt-4o-mini"
    ticket_model: str = "gpt-4o-mini"
    tool_model: str = "gpt-4o-mini"
    validator_model: str = "gpt-4o-mini"
    
    # ERP API Configuration
    erp_api_base_url: str = os.getenv("ERP_API_BASE_URL", "http://localhost:8000/api")
    erp_api_key: str = os.getenv("ERP_API_KEY", "")
    
    # Vector Store
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./vector_store")

    # RAG source documents (flat folder of .md files)
    docs_dir: str = os.getenv("DOCS_DIR", os.path.join(ROOT_DIR, "rag_data"))
    
    # Simple limits
    max_retries: int = 2
    max_tool_calls: int = 5
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

config = Config()