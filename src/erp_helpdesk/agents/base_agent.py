from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain_openai import ChatOpenAI
import json
import re
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, model_name: str, temperature: float = 0.0):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
        )

    @staticmethod
    def parse_json(text: str) -> Any:
        """Parse a model's JSON reply, tolerating ```json fences around it.

        Raises json.JSONDecodeError if the content still isn't valid JSON.
        """
        text = text.strip()
        fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
        if fenced:
            text = fenced.group(1)
        return json.loads(text)

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input and return structured output."""
        pass