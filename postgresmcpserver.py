import asyncio
import os
import sys
import warnings
from datetime import datetime

from langchain_ollama import ChatOllama
from mcp import StdioServerParameters, stdio_client, ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from prompts import system_prompt


class PostgresMCPServer:
    def __init__(self, region="us-east-1"):
        self.system_prompt = system_prompt
        self.llm = ChatOllama(
            model="llama3.1",
            base_url="http://localhost:11434"
        )
        self.server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-postgres",
                "postgres://postgres:postgres@localhost:5432/postgres"
            ],
        )

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        warnings.filterwarnings("ignore", category=RuntimeWarning, message="Cancelling an overlapped future failed")

    async def run_agent(self, question: str, thread_id: str) -> str:
        date_time = datetime.now().strftime("%Y-%m-%d %A")
        system_prompt = self.system_prompt.format(datetime=date_time)
        content = ""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                agent = create_react_agent(self.llm, tools, prompt=system_prompt)
                agent_response = await agent.ainvoke(
                    {"messages": [HumanMessage(content=question)]},
                    {"configurable": {"thread_id": thread_id}, "recursion_limit": 50},
                    print_mode=['messages']
                )
                content = agent_response["messages"][-1].content

        return content
