import os
import requests
from typing import Any, Optional
from opendesk.llm.base import LLMBackend, LLMResponse


class OpenAIBackend(LLMBackend):
    """OpenAI API backend"""
    
    def __init__(self, model: str = None, api_key: str = None):
        self._model = model
        self._api_key = api_key
    
    @property
    def name(self) -> str:
        return f"OpenAI ({self.model})"
    
    @property
    def description(self) -> str:
        return "OpenAI API"
    
    @property
    def model(self) -> str:
        if self._model:
            return self._model
        return os.environ.get("OPENAI_MODEL", "gpt-4")
    
    @property
    def api_key(self) -> str:
        if self._api_key:
            return self._api_key
        return os.environ.get("OPENAI_API_KEY", "")
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is set"""
        return bool(self.api_key)
    
    def format_tools_for_llm(self, tools: list[dict]) -> list[dict]:
        """Format tools for OpenAI"""
        formatted = []
        for tool in tools:
            formatted.append({
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {})
                }
            })
        return formatted
    
    def chat(self, prompt: str, tools: list[dict], history: list[dict] = None) -> LLMResponse:
        """Send prompt to OpenAI API"""
        if not self.is_available():
            return LLMResponse(
                content="OpenAI API key not set. Set OPENAI_API_KEY environment variable.",
                tool_calls=[]
            )
        
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        
        formatted_tools = self.format_tools_for_llm(tools)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
        }
        
        if formatted_tools:
            payload["tools"] = formatted_tools
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]
            message = choice["message"]
            
            content = message.get("content", "")
            tool_calls = []
            
            if message.get("tool_calls"):
                for call in message["tool_calls"]:
                    tool_calls.append({
                        "name": call["function"]["name"],
                        "arguments": call["function"]["arguments"]
                    })
            
            return LLMResponse(content=content, tool_calls=tool_calls)
            
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                tool_calls=[]
            )


class AnthropicBackend(LLMBackend):
    """Anthropic API backend"""
    
    def __init__(self, model: str = None, api_key: str = None):
        self._model = model
        self._api_key = api_key
    
    @property
    def name(self) -> str:
        return f"Anthropic ({self.model})"
    
    @property
    def description(self) -> str:
        return "Anthropic API (Claude)"
    
    @property
    def model(self) -> str:
        if self._model:
            return self._model
        return os.environ.get("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    
    @property
    def api_key(self) -> str:
        if self._api_key:
            return self._api_key
        return os.environ.get("ANTHROPIC_API_KEY", "")
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def chat(self, prompt: str, tools: list[dict], history: list[dict] = None) -> LLMResponse:
        if not self.is_available():
            return LLMResponse(
                content="Anthropic API key not set. Set ANTHROPIC_API_KEY.",
                tool_calls=[]
            )
        
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
        }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["content"][0].get("text", "")
            
            return LLMResponse(content=content, tool_calls=[])
            
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                tool_calls=[]
            )