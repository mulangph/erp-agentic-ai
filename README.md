# ERP Helpdesk Agentic AI
A production-ready, multi-modal agentic AI system for automating ERP helpdesk operations. This intelligent system can handle support queries, create tickets from error reports, and answer data inquiries - all with the power of AI and the safety of a built-in "Devil's Advocate" validation system.


## ✨ Features

### 🤖 Multi-Agent Architecture
- **RouterAgent** - Smart query classification (Support, Error, Data Inquiry)
- **RAGAgent** - RAG-powered support with documentation retrieval
- **TicketAgent** - Automated ticket creation with severity detection
- **ToolAgent** - ERP data request via API
- **Validator** - Response validation with Devil's Advocate double-check

### 📷 Multi-Modal Support
- Upload screenshots of errors or UI issues
- Vision-capable agents analyze images for better assistance
- OCR fallback for text extraction from images

### 🛡️ Built-in Safety
- "Devil's Advocate" double-check on all responses
- Severity-based ticket classification
- Professional, empathetic response formatting

### 🔧 Technical Capabilities
- RAG (Retrieval-Augmented Generation) with ChromaDB
- Multi-modal LLM support (GPT-4o Vision)
- Modular agent architecture
- Session management
- Mock ERP API for testing

---



Feature	How It's Implemented
Clean Architecture:	Each agent is a separate class with a process() method
Cost Tracking:	_track_cost_and_run() wrapper monitors token usage
Double-Check (Devil's Advocate):	Validator agent's prompt explicitly forces 3 mitigations
Budget Limits:	Configurable via config.max_token_budget
Retry Logic:	BaseAgent includes max_retries
Langchain Tool Calling:	Data seer agent uses create_openai_tools_agent
Vector Store:	ChromaDB with OpenAI embeddings
UI	Gradio with session management

## Setup Instructions
1. **Clone the repository**
2. Install uv
pip install uv
3. Initialize project
uv init
4. Install dependencies
uv sync
5. Set up environment variables
cp .env.example .env
Edit .env with your OpenAI API key and ERP API details
6. Seed the vector store (first run will automatically seed with sample docs)
This happens automatically when RAGAgent is first used
7. Run the application
uv run main.py


## Future Enhancements
1. Search for duplicate tickets
2. Use MCP for tool calling
3. Use postgrevector, pinecone(For production)
4. Cost tracking and limiting
5. Add test, evaluation