"""Error abstractions for opendesk.

Never leak stack traces or internal paths to MCP clients.
"""


class OpendeskError(Exception):
    def __init__(self, message: str, suggestion: str = None, code: str = None):
        self.message = message
        self.suggestion = suggestion
        self.code = code or "opendesk_error"
        super().__init__(message)


class PathSafetyError(OpendeskError):
    pass


class PermissionDeniedError(OpendeskError):
    pass


class UserDeclinedError(OpendeskError):
    pass


class RateLimitError(OpendeskError):
    pass


class ToolTimeoutError(OpendeskError):
    pass