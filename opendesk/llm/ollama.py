import os
import socket
from typing import Any, Optional
from opendesk.llm.base import LLMBackend, LLMResponse


class OllamaBackend(LLMBackend):
    """Ollama local LLM backend"""
    
    def __init__(self, model: str = None, host: str = "localhost:11434"):
        self._model = model
        self._host = host
        self._client = None
    
    @property
    def name(self) -> str:
        return f"Ollama ({self.model})"
    
    @property
    def description(self) -> str:
        return "Local, free, private"
    
    @property
    def model(self) -> str:
        if self._model:
            return self._model
        # Try to get from config or default
        return os.environ.get("OLLAMA_MODEL", "llama3.2")
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            # Try to connect to Ollama
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _get_client(self):
        """Lazy load ollama client"""
        if self._client is None:
            try:
                import ollama
                self._client = ollama
            except ImportError:
                raise ImportError("ollama package not installed. Run: pip install ollama")
        return self._client
    
    def format_tools_for_llm(self, tools: list[dict]) -> list[dict]:
        """Format tools for Ollama"""
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
        """Send prompt to Ollama and get response"""
        client = self._get_client()
        
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        
        formatted_tools = self.format_tools_for_llm(tools)
        
        try:
            response = client.chat(
                model=self.model,
                messages=messages,
                tools=formatted_tools if formatted_tools else None
            )
            
            content = response.message.content
            tool_calls = []
            
            if response.message.tool_calls:
                for call in response.message.tool_calls:
                    args = call.function.arguments
                    # Handle both dict and string arguments
                    if isinstance(args, str):
                        import json
                        try:
                            args = json.loads(args)
                        except:
                            args = {}
                    tool_calls.append({
                        "name": call.function.name,
                        "arguments": args
                    })
            
            return LLMResponse(content=content, tool_calls=tool_calls)
            
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                tool_calls=[]
            )
