"""opendesk — AI desktop control via MCP."""

def tool(tags: list[str] = None):
    """Mark a function as an opendesk tool."""
    def decorator(func):
        func._opendesk_tool = True
        func._opendesk_tags = tags or []
        return func
    if callable(tags):
        func = tags
        func._opendesk_tool = True
        func._opendesk_tags = []
        return func
    return decorator


__version__ = "1.0.0"
__all__ = ["tool", "__version__"]
