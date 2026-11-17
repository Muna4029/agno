from __future__ import annotations

from agno.models.message import Message


class AgentRunException(Exception):
    def __init__(
        self,
        exc,
        user_message: str | Message | None = None,
        agent_message: str | Message | None = None,
        messages: list[dict | Message] | None = None,
        stop_execution: bool = False,
    ):
        super().__init__(exc)
        self.user_message = user_message
        self.agent_message = agent_message
        self.messages = messages
        self.stop_execution = stop_execution


class RetryAgentRun(AgentRunException):
    """Exception raised when a tool call should be retried."""

    def __init__(
        self,
        exc,
        user_message: str | Message | None = None,
        agent_message: str | Message | None = None,
        messages: list[dict | Message] | None = None,
    ):
        super().__init__(
            exc, user_message=user_message, agent_message=agent_message, messages=messages, stop_execution=False
        )


class StopAgentRun(AgentRunException):
    """Exception raised when an agent should stop executing entirely."""

    def __init__(
        self,
        exc,
        user_message: str | Message | None = None,
        agent_message: str | Message | None = None,
        messages: list[dict | Message] | None = None,
    ):
        super().__init__(
            exc, user_message=user_message, agent_message=agent_message, messages=messages, stop_execution=True
        )


class RunCancelledException(Exception):
    """Exception raised when a run is cancelled."""

    def __init__(self, message: str = "Operation cancelled by user"):
        super().__init__(message)


class AgnoError(Exception):
    """Exception raised when an internal error occurs."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        return str(self.message)


class ModelProviderError(AgnoError):
    """Exception raised when a model provider returns an error."""

    def __init__(
        self, message: str, status_code: int = 502, model_name: str | None = None, model_id: str | None = None
    ):
        super().__init__(message, status_code)
        self.model_name = model_name
        self.model_id = model_id


class ModelRateLimitError(ModelProviderError):
    """Exception raised when a model provider returns a rate limit error."""

    def __init__(
        self, message: str, status_code: int = 429, model_name: str | None = None, model_id: str | None = None
    ):
        super().__init__(message, status_code, model_name, model_id)


class EvalError(Exception):
    """Exception raised when an evaluation fails."""
