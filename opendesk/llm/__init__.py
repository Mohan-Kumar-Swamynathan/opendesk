from opendesk.llm.base import LLMBackend, LLMResponse
from opendesk.llm.ollama import OllamaBackend
from opendesk.llm.claude_mcp import ClaudeMCPBackend
from opendesk.llm.openai import OpenAIBackend
from opendesk.llm.custom import CustomHTTPBackend
from opendesk.llm.direct import DirectBackend

__all__ = [
    "LLMBackend",
    "LLMResponse",
    "OllamaBackend",
    "ClaudeMCPBackend", 
    "OpenAIBackend",
    "CustomHTTPBackend",
    "DirectBackend",
    "get_available_backends",
    "get_backend_by_name",
]


def get_available_backends():
    """Detect and return all available LLM backends"""
    backends = []
    seen_names = set()
    
    # Check each backend
    for backend_class in [OllamaBackend, ClaudeMCPBackend, OpenAIBackend, CustomHTTPBackend]:
        try:
            backend = backend_class()
            if backend.is_available() and backend.name not in seen_names:
                backends.append(backend)
                seen_names.add(backend.name)
        except Exception:
            pass
    
    return backends


def get_backend_by_name(name: str):
    """Get backend by name, case-insensitive"""
    name_lower = name.lower().strip()
    
    backends_map = {
        "ollama": OllamaBackend,
        "claude": ClaudeMCPBackend,
        "claude-mcp": ClaudeMCPBackend,
        "mcp": ClaudeMCPBackend,
        "openai": OpenAIBackend,
        "custom": CustomHTTPBackend,
        "http": CustomHTTPBackend,
        "direct": DirectBackend,
        "none": DirectBackend,
        "keyword": DirectBackend,
    }
    
    backend_class = backends_map.get(name_lower)
    if backend_class:
        return backend_class()
    return None
