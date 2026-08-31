from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, model_name: str, temperature: float = 0.0):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
        )
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input and return structured output."""
        pass