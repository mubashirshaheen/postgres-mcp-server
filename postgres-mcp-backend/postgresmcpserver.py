"""postgresmcpserver.py enforcing table-only responses."""
import importlib
import json
from datetime import datetime
from typing import Any

from langchain_aws import ChatBedrockConverse
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from mcp import StdioServerParameters, stdio_client, ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage

import config
from custom_tools import get_component_tool, get_supplier_tool, list_columns_tool, list_tables_tool, \
    get_large_array_tool, create_excel
from prompts.prompt_bedrock import system_prompt


class PostgresMCPServer:
    """PostgresMCPServer integrates a language model with a PostgreSQL database using MCP."""

    def __init__(self, region):
        self.app_name = config.APP_NAME
        if self.app_name == "TPS":
            print("Loading TPS schema...")
            schema_module = importlib.import_module("prompts.prompts_tps.schema_tps_prompt_partial")
        else:
            print("Loading Alias schema...")
            schema_module = importlib.import_module("prompts.prompts_alias.schema_alias_prompt")
        self.schema = schema_module.schema
        self.system_prompt = system_prompt + (
            "\n## FINAL HARD RULE\n"
            "Return ONLY LIST OF JSON or JSON or 'No data found for the given criteria.'\n"
            "If you produce any other format, it will be discarded.\n"
        )
        self.llm = ChatBedrockConverse(
            model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            region_name=region,
            # credentials_profile_name="test"
        )
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres", config.DB_URL],
        )

    async def run_agent(self, question: str, thread_id: str) -> dict[str, Any]:
        """
        :param question:
        :param thread_id:
        :return:
        """
        if question in ["hi", "hello"]:
            return {"data": "Hello! How can I assist you with the database today?"}
        date_time = str(datetime.now())
        system_prompt_formatted = self.system_prompt.replace("{datetime}", date_time) + self.schema
        content = ""

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                mcp_tools = await load_mcp_tools(session)
                tools = mcp_tools + [get_large_array_tool, get_component_tool,
                                     create_excel,
                                     get_supplier_tool]

                agent = create_agent(
                    self.llm,
                    tools,
                    system_prompt=system_prompt_formatted
                )

                agent_response = await agent.ainvoke(
                    {"messages": [HumanMessage(content=question)]},
                    RunnableConfig(configurable={"thread_id": thread_id}, recursion_limit=30),
                    print_mode=['messages']
                )

                raw_content = agent_response["messages"][-1].content or agent_response["messages"][-2].content

                if "No data found" in raw_content:
                    content = "No data found for the given criteria."
                elif isinstance(raw_content, list):
                    content = raw_content
                else:
                    content = json.loads(raw_content)

            if isinstance(content, dict):
                return content
            if content[0].get('type') == "text":
                content = json.loads(content[0].get('text', []))[0].get('message')

        return {"data": content}
