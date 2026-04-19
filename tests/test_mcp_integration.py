import pytest
import asyncio


@pytest.mark.asyncio
async def test_tools_list():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async with stdio_client(
        StdioServerParameters(command="opendesk", args=["--serve"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert len(tools.tools) >= 10
            tool_names = [t.name for t in tools.tools]
            assert "take_screenshot" in tool_names
            assert "run_command" in tool_names


@pytest.mark.asyncio
async def test_system_info_tool():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async with stdio_client(
        StdioServerParameters(command="opendesk", args=["--serve"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_system_info", {})
            assert result.content is not None


@pytest.mark.asyncio
async def test_list_processes():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async with stdio_client(
        StdioServerParameters(command="opendesk", args=["--serve"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("list_processes", {"limit": 5})
            assert result.content is not None