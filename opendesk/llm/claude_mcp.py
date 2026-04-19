import os
import asyncio
from typing import Any, Optional
from opendesk.llm.base import LLMBackend, LLMResponse


class ClaudeMCPBackend(LLMBackend):
    """Claude Desktop via MCP backend"""
    
    def __init__(self, mcp_command: str = "opendesk", mcp_args: list = None):
        self._mcp_command = mcp_command
        self._mcp_args = mcp_args or ["--serve"]
        self._session = None
    
    @property
    def name(self) -> str:
        return "Claude (MCP)"
    
    @property
    def description(self) -> str:
        return "Via MCP server"
    
    def is_available(self) -> bool:
        """Check if we can connect to MCP server"""
        # Try to import MCP client
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            return True
        except ImportError:
            return False
    
    def _get_session(self):
        """Get or create MCP session"""
        if self._session is None:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            return ClientSession, StdioServerParameters, stdio_client
        return self._session
    
    def format_tools_for_llm(self, tools: list[dict]) -> list[dict]:
        """Format tools for Claude"""
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
    
    async def _chat_async(self, prompt: str, tools: list[dict], history: list[dict] = None) -> LLMResponse:
        """Send prompt to Claude via MCP"""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        
        formatted_tools = self.format_tools_for_llm(tools)
        
        try:
            async with stdio_client(
                StdioServerParameters(
                    command=self._mcp_command,
                    args=self._mcp_args
                )
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Get tools list
                    tools_result = await session.list_tools()
                    available_tools = [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.inputSchema
                        }
                        for t in tools_result.tools
                    ]
                    
                    # Call tool - just get system info for now as test
                    # Claude will respond with tool calls in its message
                    result = await session.call_tool("get_system_info", {})
                    
                    return LLMResponse(
                        content=str(result.content),
                        tool_calls=[]
                    )
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                tool_calls=[]
            )
    
    def chat(self, prompt: str, tools: list[dict], history: list[dict] = None) -> LLMResponse:
        """Synchronous wrapper for MCP chat"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self._chat_async(prompt, tools, history)
                    )
                    return future.result()
            else:
                return asyncio.run(self._chat_async(prompt, tools, history))
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                tool_calls=[]
            )