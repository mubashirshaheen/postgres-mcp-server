"""Revised postgresmcpserver.py enforcing table-only responses."""
import json
import os
from datetime import datetime

from langchain_aws import ChatBedrockConverse
from langgraph.prebuilt import create_react_agent
from mcp import StdioServerParameters, stdio_client, ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage


from custom_tools import get_component_tool, get_supplier_tool, list_columns_tool, list_tables_tool, \
    get_large_array_tool, create_excel, count_products_tool, create_chart_products
from prompts.prompt_bedrock import system_prompt
from prompts.prompts_tps.schema_tps_prompt_partial import schema
from prompts.prompts_tps.specific_prompt import specific_prompt


class PostgresMCPServer:
    """PostgresMCPServer integrates a language model with a PostgreSQL database using MCP."""
    def __init__(self, region="us-east-1"):
        self.system_prompt = system_prompt + (
            "\n## FINAL HARD RULE\n"
            "Return ONLY LIST OF JSON or 'No data found for the given criteria.'\n"
            "If you produce any other format, it will be discarded.\n"
        )
        self.llm = ChatBedrockConverse(
            model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            region_name=region,
            credentials_profile_name="test"
        )
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres", os.getenv("DB_URL")],
        )

    async def run_agent(self, question: str, thread_id: str) -> str:
        """

        :param question:
        :param thread_id:
        :return:
        """
        date_time = datetime.now().strftime("%Y-%m-%d %A")
        system_prompt_formatted = self.system_prompt.replace("{datetime}", date_time) + schema + specific_prompt
        content = ""

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                mcp_tools = await load_mcp_tools(session)
                tools = mcp_tools + [list_tables_tool, list_columns_tool,
                                     get_large_array_tool, create_chart_products,
                                     get_supplier_tool, create_excel, count_products_tool]

                agent = create_react_agent(
                    self.llm,
                    tools,
                    prompt=system_prompt_formatted
                )

                agent_response = await agent.ainvoke(
                    {"messages": [HumanMessage(content=question)]},
                    {"configurable": {"thread_id": thread_id}, "recursion_limit": 10},
                    print_mode=['messages']
                )

                raw_content = agent_response["messages"][-1].content or agent_response["messages"][-2].content

                if "No data found" in raw_content:
                    content = "No data found for the given criteria."
                elif isinstance(raw_content, list):
                    content = raw_content
                elif raw_content.startswith("/"):
                    content = {"file_path": raw_content}
                else:
                    # print(raw_content)
                    content = json.loads(raw_content)

        return content
