import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    async with stdio_client(
        StdioServerParameters(command="opendesk", args=["--serve"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()

            ollama_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
                for t in tools.tools
            ]

            print(f"opendesk ready. Tools loaded: {len(ollama_tools)}")
            print("Type your command (or 'quit'):")

            while True:
                user_input = input("> ")
                if user_input.lower() == "quit":
                    break

                response = ollama.chat(
                    model="llama3.2",
                    messages=[{"role": "user", "content": user_input}],
                    tools=ollama_tools
                )

                if response.message.tool_calls:
                    for call in response.message.tool_calls:
                        result = await session.call_tool(
                            call.function.name,
                            {}
                        )
                        print(f"[{call.function.name}]:", result.content[0].text[:300])
                else:
                    print(response.message.content)


if __name__ == "__main__":
    asyncio.run(main())