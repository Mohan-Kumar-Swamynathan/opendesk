from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LLMResponse:
    """Response from an LLM"""
    content: str
    tool_calls: list[dict[str, Any]]
    
    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMBackend(ABC):
    """Abstract base class for all LLM backends"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for the backend"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Short description shown in menu"""
        pass
    
    @property
    def short_id(self) -> str:
        """Short identifier for selection"""
        return self.name.lower().replace(" ", "-")
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this LLM is accessible"""
        pass
    
    @abstractmethod
    def chat(self, prompt: str, tools: list[dict], history: list[dict] = None) -> LLMResponse:
        """
        Send a prompt and get a response with optional tool calls.
        
        Args:
            prompt: User's message
            tools: List of tool definitions (MCP tool format)
            history: Optional conversation history
            
        Returns:
            LLMResponse with content and tool_calls
        """
        pass
    
    def format_tools_for_llm(self, tools: list[dict]) -> list[dict]:
        """Format tools for the specific LLM API"""
        return tools
    
    def format_history(self, history: list[dict]) -> list[dict]:
        """Format conversation history for the LLM"""
        return history or []


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
            # This will execute and return result
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
