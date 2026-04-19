"""Start MCP server."""
import logging
import sys

logger = logging.getLogger(__name__)


def run_serve(transport: str = "stdio", port: int = 8765):
    """Start MCP server in requested mode."""
    from opendesk.server import get_server

    server = get_server()
    logger.info(f"Starting opendesk MCP server (transport={transport})")

    try:
        if transport == "stdio":
            server.run(transport="stdio")
        elif transport == "streamable-http":
            server.run(transport="streamable-http", port=port)
        else:
            logger.error(f"Unknown transport: {transport}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped.")
    except Exception as e:
        logger.exception(f"Server crashed: {e}")
        sys.exit(1)