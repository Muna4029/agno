"""Run `pip install openai yfinance` to install dependencies."""    

# Note: Currently, Llama API does not support tools with parameters other than string.
# This is a limitation of the Llama API.

import asyncio

from agno.agent import Agent
from agno.models.meta import LlamaOpenAI

agent = None

if __name__ == "__main__":
    try:
        from agno.tools.yfinance import YFinanceTools
        tools = [YFinanceTools()]
    except Exception:
        tools = []

    agent = Agent(
        model=LlamaOpenAI(id="Llama-4-Maverick-17B-128E-Instruct-FP8"),
        tools=tools,
        show_tool_calls=True,
    )
    asyncio.run(agent.aprint_response("Whats the price of AAPL stock?"))
