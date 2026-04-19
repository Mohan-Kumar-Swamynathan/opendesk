import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def morning_routine():
    async with stdio_client(
        StdioServerParameters(command="opendesk", args=["--serve"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Good morning! Running your routine...")

            result = await session.call_tool("get_system_info", {})
            print(f"System: {result.content}")

            result = await session.call_tool("send_notification", {
                "title": "Good Morning!",
                "message": "Your AI assistant is ready to help."
            })
            print(f"Notification: {result.content}")

            result = await session.call_tool("get_clipboard", {})
            print(f"Clipboard: {result.content}")

            result = await session.call_tool("list_recent_files", {
                "days": 1,
                "max_results": 5
            })
            print(f"Recent files: {result.content}")


if __name__ == "__main__":
    asyncio.run(morning_routine())