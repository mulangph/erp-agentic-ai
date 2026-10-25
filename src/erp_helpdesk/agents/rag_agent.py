import json
import os
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from erp_helpdesk.agents.base_agent import BaseAgent
from erp_helpdesk.config import config
import logging

logger = logging.getLogger(__name__)

class RAGAgent(BaseAgent):
    """Agent 2: RAG agent with multi-modal support."""
    
    def __init__(self):
        super().__init__(model_name=config.rag_model, temperature=0.2)
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=config.chroma_persist_dir,
            embedding_function=self.embeddings,
            collection_name="erp_docs"
        )
        # Vision model for image analysis
        self.vision_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2
        )
        # Seed the vector store
        self._seed_vector_store()
        
    def _seed_vector_store(self):
        """Seed vector store with documentation loaded from categorized .md files."""
        try:
            # Check if collection exists and has documents
            try:
                count = self.vector_store._collection.count()
                if count > 0:
                    logger.info(f"Vector store already has {count} documents")
                    return
            except:
                pass
            
            # config.docs_dir points to a flat folder of .md files, e.g.:
            #   rag_data/purchase-orders.md
            #   rag_data/stock-management.md
            docs_dir = config.docs_dir
            md_files = glob.glob(os.path.join(docs_dir, "*.md"))
            
            if not md_files:
                logger.warning(f"No markdown documentation files found in {docs_dir}")
                return
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
            
            documents: List[Document] = []
            for file_path in md_files:
                source_name = Path(file_path).stem
                # Files are flat (no category subfolders), so derive a readable
                # category label from the filename itself, e.g.
                # "purchase-orders" -> "Purchase Orders"
                category = source_name.replace("-", " ").replace("_", " ").title()
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                chunks = splitter.split_text(content)
                for i, chunk in enumerate(chunks):
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            "source": source_name,
                            "category": category,
                            "file_path": file_path,
                            "chunk_index": i
                        }
                    ))
            
            # langchain_chroma persists automatically when persist_directory is set
            self.vector_store.add_documents(documents)
            logger.info(f"Vector store seeded with {len(documents)} chunks from {len(md_files)} markdown files")
            
        except Exception as e:
            logger.warning(f"Could not seed vector store: {e}")
    
    def _analyze_screenshot(self, image_data: Dict) -> str:
        """Analyze screenshot for UI guidance."""
        if not image_data or not image_data.get("base64"):
            return None
            
        try:
            prompt = """Analyze this ERP screenshot and provide specific guidance:
            
            1. What screen/module is this?
            2. What fields are visible?
            3. What actions can the user take here?
            4. Based on this screenshot, what might the user need help with?
            """
            
            response = self.vision_llm.invoke([
                HumanMessage(content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data['base64']}"}}
                ])
            ])
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Screenshot analysis failed: {e}")
            return None
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_message = input_data.get("original_message", "")
        user_id = input_data.get("user_id", "anonymous")
        image_data = input_data.get("image")
        image_context = input_data.get("image_context", "")
        
        logger.info(f"RAGAgent processing support request from {user_id}")
        
        # Analyze screenshot if provided
        screenshot_analysis = None
        if image_data:
            screenshot_analysis = self._analyze_screenshot(image_data)
            logger.info(f"Screenshot analysis: {screenshot_analysis[:200] if screenshot_analysis else 'None'}")
        
        # Retrieve relevant docs
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # Build enhanced query with image context
        enhanced_query = user_message
        if screenshot_analysis:
            enhanced_query += f"\n\n[Screenshot shows: {screenshot_analysis}]"
        if image_context:
            enhanced_query += f"\n\n[Image context: {image_context}]"
        
        retrieved_docs = retriever.invoke(enhanced_query)
        context = "\n\n".join([
            f"[Source: {doc.metadata.get('source', 'unknown')} | Category: {doc.metadata.get('category', 'general')}]\n{doc.page_content}"
            for doc in retrieved_docs
        ])
        
        # Track the actual source document(s) retrieved from the vector store,
        # so we can report real sources rather than relying only on the LLM.
        retrieved_sources = list(dict.fromkeys(
            doc.metadata.get("source", "unknown") for doc in retrieved_docs
        ))
        
        # Generate response
        system_prompt = """You are a support expert for an ERP system.
        
        TASK:
        1. Use the provided documentation context to answer the user's question.
        2. If a screenshot is provided, use the analysis to give more specific guidance.
        5. Be specific and step-by-step.
        
        Output format (JSON):
        {
            "answer": "Your detailed, step-by-step answer here...",
            "rm_sample": "```rm\\n# Your RubyMarkup sample here\\n```" or null,
            "sources": ["source1", "source2"],
            "visual_guidance": "If screenshot provided, give additional visual guidance here" or null
        }
        
        IMPORTANT: Return ONLY the JSON object, no other text.
        """
        
        def _generate():
            message_content = f"User Question: {user_message}\n\nDocumentation Context:\n{context}"
            
            if screenshot_analysis:
                message_content += f"\n\nScreenshot Analysis: {screenshot_analysis}"
            
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=message_content)
            ])
            
            try:
                return self.parse_json(response.content)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON, using default. Response: {response.content[:200]}")
                return {
                    "answer": response.content,
                    "rm_sample": None,
                    "sources": [],
                    "visual_guidance": None
                }
        
        result = _generate()
        
        # Merge the actual retrieved source documents with whatever the LLM
        # itself reported, de-duplicated and with retrieved sources listed first.
        llm_sources = result.get("sources", [])
        combined_sources = list(dict.fromkeys(retrieved_sources + llm_sources))
        
        return {
            "status": "success",
            "category": "SUPPORT",
            "answer": result.get("answer", "I couldn't generate a response."),
            "rm_sample": result.get("rm_sample"),
            "sources": combined_sources,
            "visual_guidance": result.get("visual_guidance"),
            "screenshot_analysis": screenshot_analysis,
            "user_id": user_id,
            "original_message": user_message,
            "image": image_data
        }