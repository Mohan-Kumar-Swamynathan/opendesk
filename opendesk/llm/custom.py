import os
import requests
from typing import Any, Optional
from opendesk.llm.base import LLMBackend, LLMResponse


class CustomHTTPBackend(LLMBackend):
    """Custom OpenAI-compatible API backend"""
    
    def __init__(self, url: str = None, api_key: str = None, model: str = None):
        self._url = url
        self._api_key = api_key
        self._model = model
    
    @property
    def name(self) -> str:
        return f"Custom ({self.model or 'unknown'})"
    
    @property
    def description(self) -> str:
        return "OpenAI-compatible API"
    
    @property
    def url(self) -> str:
        if self._url:
            return self._url
        return os.environ.get("CUSTOM_LLM_URL", "")
    
    @property
    def api_key(self) -> str:
        if self._api_key:
            return self._api_key
        return os.environ.get("CUSTOM_LLM_API_KEY", "")
    
    @property
    def model(self) -> str:
        if self._model:
            return self._model
        return os.environ.get("CUSTOM_LLM_MODEL", "gpt-3.5-turbo")
    
    def is_available(self) -> bool:
        """Check if custom endpoint is configured"""
        return bool(self.url)
    
    def format_tools_for_llm(self, tools: list[dict]) -> list[dict]:
        """Format tools for OpenAI-compatible API"""
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
        """Send prompt to custom OpenAI-compatible API"""
        if not self.is_available():
            return LLMResponse(
                content="Custom LLM not configured. Set CUSTOM_LLM_URL environment variable.",
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
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            if "openai" in self.url.lower():
                headers["Authorization"] = f"Bearer {self.api_key}"
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                f"{self.url.rstrip('/')}/v1/chat/completions",
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


class LMStudioBackend(CustomHTTPBackend):
    """LM Studio local backend"""
    
    def __init__(self):
        super().__init__(
            url="http://localhost:1234/v1",
            model=os.environ.get("LMSTUDIO_MODEL", "local-model")
        )
    
    @property
    def name(self) -> str:
        return "LM Studio"
    
    @property
    def description(self) -> str:
        return "Local (LM Studio)"
    
    def is_available(self) -> bool:
        try:
            import requests
            resp = requests.get("http://localhost:1234/v1/models", timeout=2)
            return resp.status_code == 200
        except:
            return False


class OllamaWebBackend(CustomHTTPBackend):
    """Ollama web API (when using ollama webui)"""
    
    def __init__(self, url: str = "http://localhost:11434"):
        super().__init__(
            url=url,
            model=os.environ.get("OLLAMA_WEB_MODEL", "llama2")
        )
    
    @property
    def name(self) -> str:
        return "Ollama Web"
    
    @property
    def description(self) -> str:
        return "Ollama via HTTP"
    
    def is_available(self) -> bool:
        try:
            import requests
            resp = requests.get(f"{self.url}/api/tags", timeout=2)
            return resp.status_code == 200
        except:
            return False
