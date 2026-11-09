from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from os import getenv
from typing import Any

from pydantic import BaseModel

from agno.exceptions import ModelProviderError
from agno.models.base import MessageData, Model, _add_usage_metrics_to_assistant_message
from agno.models.message import Message
from agno.models.response import ModelResponse
from agno.utils.log import log_debug, log_error
from agno.utils.models.cohere import format_messages

try:
    from cohere import AsyncClientV2 as CohereAsyncClient
    from cohere import ClientV2 as CohereClient
    from cohere.types.chat_response import ChatResponse
    from cohere.types.streamed_chat_response_v2 import StreamedChatResponseV2
except ImportError:
    raise ImportError("`cohere` not installed. Please install using `pip install cohere`")


@dataclass
class Cohere(Model):
    """
    A class representing the Cohere model.

    For more information, see: https://docs.cohere.com/docs/chat-api
    """

    id: str = "command-r-plus"
    name: str = "cohere"
    provider: str = "Cohere"

    # -*- Request parameters
    temperature: float | None = None
    max_tokens: int | None = None
    top_k: int | None = None
    top_p: float | None = None
    seed: int | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    logprobs: bool | None = None
    request_params: dict[str, Any] | None = None
    strict_tools: bool = False
    # Add chat history to the cohere messages instead of using the conversation_id
    add_chat_history: bool = False
    # -*- Client parameters
    api_key: str | None = None
    client_params: dict[str, Any] | None = None
    # -*- Provide the Cohere client manually
    client: CohereClient | None = None
    async_client: CohereAsyncClient | None = None

    def get_client(self) -> CohereClient:
        if self.client:
            return self.client

        _client_params: dict[str, Any] = {}

        self.api_key = self.api_key or getenv("CO_API_KEY")
        if not self.api_key:
            log_error("CO_API_KEY not set. Please set the CO_API_KEY environment variable.")

        _client_params["api_key"] = self.api_key

        self.client = CohereClient(**_client_params)
        return self.client  # type: ignore

    def get_async_client(self) -> CohereAsyncClient:
        if self.async_client:
            return self.async_client

        _client_params: dict[str, Any] = {}

        self.api_key = self.api_key or getenv("CO_API_KEY")

        if not self.api_key:
            log_error("CO_API_KEY not set. Please set the CO_API_KEY environment variable.")

        _client_params["api_key"] = self.api_key

        self.async_client = CohereAsyncClient(**_client_params)
        return self.async_client  # type: ignore

    def get_request_params(
        self,
        response_format: dict | type[BaseModel] | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        _request_params: dict[str, Any] = {}
        if self.temperature:
            _request_params["temperature"] = self.temperature
        if self.max_tokens:
            _request_params["max_tokens"] = self.max_tokens
        if self.top_k:
            _request_params["k"] = self.top_k
        if self.top_p:
            _request_params["p"] = self.top_p
        if self.seed:
            _request_params["seed"] = self.seed
        if self.logprobs:
            _request_params["logprobs"] = self.logprobs
        if self.frequency_penalty:
            _request_params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty:
            _request_params["presence_penalty"] = self.presence_penalty

        if response_format:
            _request_params["response_format"] = response_format

        # Format tools
        if tools is not None and len(tools) > 0:
            formatted_tools = []
            for tool in tools:
                if tool.get("type") == "function" and "function" in tool:
                    # Extract only the fields that Cohere supports
                    filtered_tool = {
                        "type": "function",
                        "function": {
                            "name": tool["function"]["name"],
                            "description": tool["function"]["description"],
                            "parameters": tool["function"]["parameters"],
                        },
                    }
                    formatted_tools.append(filtered_tool)
                else:
                    # For non-function tools, pass them through as-is
                    formatted_tools.append(tool)

            _request_params["tools"] = formatted_tools
            # Fix optional parameters where the "type" is [type, null]
            for tool in _request_params["tools"]:  # type: ignore
                if "parameters" in tool["function"] and "properties" in tool["function"]["parameters"]:  # type: ignore
                    params = tool["function"]["parameters"]
                    # Cohere requires at least one required parameter, so if unset, set it to all parameters
                    if len(params.get("required", [])) == 0:
                        params["required"] = list(params["properties"].keys())
            _request_params["strict_tools"] = self.strict_tools

        if self.request_params:
            _request_params.update(self.request_params)

        if _request_params:
            log_debug(f"Calling {self.provider} with request parameters: {_request_params}", log_level=2)
        return _request_params

    def invoke(
        self,
        messages: list[Message],
        response_format: dict | type[BaseModel] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> ChatResponse:
        """
        Invoke a non-streamed chat response from the Cohere API.
        """

        request_kwargs = self.get_request_params(response_format=response_format, tools=tools)

        try:
            return self.get_client().chat(model=self.id, messages=format_messages(messages), **request_kwargs)  # type: ignore
        except Exception as e:
            log_error(f"Unexpected error calling Cohere API: {e!s}")
            raise ModelProviderError(message=str(e), model_name=self.name, model_id=self.id) from e

    def invoke_stream(
        self,
        messages: list[Message],
        response_format: dict | type[BaseModel] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> Iterator[StreamedChatResponseV2]:
        """
        Invoke a streamed chat response from the Cohere API.
        """
        request_kwargs = self.get_request_params(response_format=response_format, tools=tools)

        try:
            return self.get_client().chat_stream(
                model=self.id,
                messages=format_messages(messages),  # type: ignore
                **request_kwargs,
            )
        except Exception as e:
            log_error(f"Unexpected error calling Cohere API: {e!s}")
            raise ModelProviderError(message=str(e), model_name=self.name, model_id=self.id) from e

    async def ainvoke(
        self,
        messages: list[Message],
        response_format: dict | type[BaseModel] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> ChatResponse:
        """
        Asynchronously invoke a non-streamed chat response from the Cohere API.
        """
        request_kwargs = self.get_request_params(response_format=response_format, tools=tools)

        try:
            return await self.get_async_client().chat(
                model=self.id,
                messages=format_messages(messages),  # type: ignore
                **request_kwargs,
            )
        except Exception as e:
            log_error(f"Unexpected error calling Cohere API: {e!s}")
            raise ModelProviderError(message=str(e), model_name=self.name, model_id=self.id) from e

    async def ainvoke_stream(
        self,
        messages: list[Message],
        response_format: dict | type[BaseModel] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> AsyncIterator[StreamedChatResponseV2]:
        """
        Asynchronously invoke a streamed chat response from the Cohere API.
        """
        request_kwargs = self.get_request_params(response_format=response_format, tools=tools)

        try:
            async for response in self.get_async_client().chat_stream(
                model=self.id,
                messages=format_messages(messages),  # type: ignore
                **request_kwargs,
            ):
                yield response
        except Exception as e:
            log_error(f"Unexpected error calling Cohere API: {e!s}")
            raise ModelProviderError(message=str(e), model_name=self.name, model_id=self.id) from e

    def parse_provider_response(self, response: ChatResponse, **kwargs) -> ModelResponse:
        """
        Parse the model provider response.

        Args:
            response (ChatResponse): The response from the Cohere API.
        """
        model_response = ModelResponse()

        model_response.role = response.message.role

        response_message = response.message
        if response_message.content is not None:
            full_content = ""
            for item in response_message.content:
                full_content += item.text
            model_response.content = full_content

        if response_message.tool_calls is not None:
            model_response.tool_calls = [t.model_dump() for t in response_message.tool_calls]

        if response.usage is not None and response.usage.tokens is not None:
            model_response.response_usage = {
                "input_tokens": int(response.usage.tokens.input_tokens) or 0,  # type: ignore
                "output_tokens": int(response.usage.tokens.output_tokens) or 0,  # type: ignore
                "total_tokens": int(response.usage.tokens.input_tokens + response.usage.tokens.output_tokens) or 0,  # type: ignore
            }

        return model_response

    def _process_stream_response(
        self,
        response: StreamedChatResponseV2,
        assistant_message: Message,
        stream_data: MessageData,
        tool_use: dict[str, Any],
    ) -> tuple[ModelResponse | None, dict[str, Any]]:
        """
        Common handler for processing stream responses from Cohere.

        Args:
            response: The streamed response from Cohere
            assistant_message: The assistant message being built
            stream_data: Data accumulated during streaming
            tool_use: Current tool use data being built

        Returns:
            Tuple containing the ModelResponse to yield and updated tool_use dict
        """
        model_response = None

        if (
            response.type == "content-delta"
            and response.delta is not None
            and response.delta.message is not None
            and response.delta.message.content is not None
        ):
            # Update metrics
            assistant_message.metrics.completion_tokens += 1
            if not assistant_message.metrics.time_to_first_token:
                assistant_message.metrics.set_time_to_first_token()

            # Update provider response content
            stream_data.response_content += response.delta.message.content.text
            model_response = ModelResponse(content=response.delta.message.content.text)

        elif response.type == "tool-call-start" and response.delta is not None:
            if response.delta.message is not None and response.delta.message.tool_calls is not None:
                tool_use = response.delta.message.tool_calls.model_dump()

        elif response.type == "tool-call-delta" and response.delta is not None:
            if (
                response.delta.message is not None
                and response.delta.message.tool_calls is not None
                and response.delta.message.tool_calls.function is not None
            ):
                tool_use["function"]["arguments"] += response.delta.message.tool_calls.function.arguments

        elif response.type == "tool-call-end":
            if assistant_message.tool_calls is None:
                assistant_message.tool_calls = []
            assistant_message.tool_calls.append(tool_use)
            tool_use = {}

        elif (
            response.type == "message-end"
            and response.delta is not None
            and response.delta.usage is not None
            and response.delta.usage.tokens is not None
        ):
            _add_usage_metrics_to_assistant_message(
                assistant_message=assistant_message,
                response_usage={
                    "input_tokens": int(response.delta.usage.tokens.input_tokens) or 0,  # type: ignore
                    "output_tokens": int(response.delta.usage.tokens.output_tokens) or 0,  # type: ignore
                    "total_tokens": int(
                        response.delta.usage.tokens.input_tokens + response.delta.usage.tokens.output_tokens  # type: ignore
                    )
                    or 0,
                },
            )

        return model_response, tool_use

    def process_response_stream(
        self,
        messages: list[Message],
        assistant_message: Message,
        stream_data: MessageData,
        response_format: dict | type[BaseModel] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> Iterator[ModelResponse]:
        """Process the synchronous response stream."""
        tool_use: dict[str, Any] = {}

        for response in self.invoke_stream(
            messages=messages, response_format=response_format, tools=tools, tool_choice=tool_choice
        ):
            model_response, tool_use = self._process_stream_response(
                response=response, assistant_message=assistant_message, stream_data=stream_data, tool_use=tool_use
            )
            if model_response is not None:
                yield model_response

    async def aprocess_response_stream(
        self,
        messages: list[Message],
        assistant_message: Message,
        stream_data: MessageData,
        response_format: dict | type[BaseModel] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> AsyncIterator[ModelResponse]:
        """Process the asynchronous response stream."""
        tool_use: dict[str, Any] = {}

        async for response in self.ainvoke_stream(
            messages=messages, response_format=response_format, tools=tools, tool_choice=tool_choice
        ):
            model_response, tool_use = self._process_stream_response(
                response=response, assistant_message=assistant_message, stream_data=stream_data, tool_use=tool_use
            )
            if model_response is not None:
                yield model_response

    def parse_provider_response_delta(self, response: Any) -> ModelResponse:  # type: ignore
        pass
