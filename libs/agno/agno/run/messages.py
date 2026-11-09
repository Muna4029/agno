from __future__ import annotations

from dataclasses import dataclass, field

from agno.models.message import Message


@dataclass
class RunMessages:
    """Container for messages used in an Agent run.

    Attributes:
        messages: List of all messages to send to the model
        system_message: The system message for this run
        user_message: The user message for this run
        extra_messages: Extra messages added after the system and user messages
    """

    messages: list[Message] = field(default_factory=list)
    system_message: Message | None = None
    user_message: Message | None = None
    extra_messages: list[Message] | None = None

    def get_input_messages(self) -> list[Message]:
        """Get the input messages for the model."""
        input_messages = []
        if self.system_message is not None:
            input_messages.append(self.system_message)
        if self.user_message is not None:
            input_messages.append(self.user_message)
        if self.extra_messages is not None:
            input_messages.extend(self.extra_messages)
        return input_messages
