from typing import Any
from opendesk.llm.base import LLMBackend, LLMResponse


class DirectBackend(LLMBackend):
    """Fallback backend that uses keyword matching (no LLM)"""
    
    @property
    def name(self) -> str:
        return "Direct"
    
    @property
    def description(self) -> str:
        return "Keyword matching (no LLM)"
    
    def is_available(self) -> bool:
        return True
    
    def chat(self, prompt: str, tools: list[dict], history: list[dict] = None) -> LLMResponse:
        """Use keyword matching to determine tool"""
        from opendesk.ai_cli import parse_ask
        try:
            parse_ask(prompt)
            return LLMResponse(
                content="Executed via direct mode",
                tool_calls=[]
            )
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                tool_calls=[]
            )
