import asyncio
import base64
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def screen_agent():
    async with stdio_client(
        StdioServerParameters(command="opendesk", args=["--serve"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Taking screenshot...")
            result = await session.call_tool("take_screenshot", {})

            import json
            data = json.loads(result.content[0].text)

            if data.get("image_base64"):
                print("Screenshot captured!")
                print(f"Size: {data.get('width', 0)}x{data.get('height', 0)}")

                image_data = base64.b64decode(data["image_base64"])
                with open("screenshot.png", "wb") as f:
                    f.write(image_data)
                print("Saved to screenshot.png")
            else:
                print("Failed to capture screenshot")


async def ocr_agent():
    async with stdio_client(
        StdioServerParameters(command="opendesk", args=["--serve"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Running OCR on screen...")
            result = await session.call_tool("get_screen_text", {})

            import json
            data = json.loads(result.content[0].text)
            print(f"Extracted text: {data.get('text', '')[:500]}")


if __name__ == "__main__":
    asyncio.run(screen_agent())