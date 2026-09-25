import os
from dotenv import load_dotenv
from langchain.agents import create_agent

from app.services.state import PriceComparisonState

# from app.services.graph import PriceComparisonState

load_dotenv()
githubagentprompt=("you are a github agent when user asks to create a branch "
                   "check the branch  and repo then invoke the create branch tool "
                   "use get me tool to know about repo ")

temp_token = os.getenv("APIFY_TOKEN")

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
# def price_comparison_node(state: PriceComparisonState) -> PriceComparisonState:
#     # Internal node with price comparison logic
#     return {"response": f"Comparing prices for: {PriceComparisonState['user_input']}..."}
async def price_comparison_node(state: PriceComparisonState):
    client = MultiServerMCPClient(
        {
            # "github": {
            #     "transport": "streamable_http",
            #     "url": "https://api.githubcopilot.com/mcp/",
            #     "headers": {
            #         "Authorization": f"Bearer {temp_token}"
            #     },
            # },
            "apify": {
                "transport": "streamable_http",
                "url": "https://mcp.apify.com",
                "headers": {
                    "Authorization": f"Bearer {temp_token}"
                },
            }

        }
    )
    tools = await client.get_tools()  # loads all GitHub MCP tools as LangChain tools

    print(tools)
    # agent = create_agent("google_genai:gemini-3.5-flash", tools,system_prompt="get accreos multiple ecommerce sites like amazon,bestbuy,wallmart and present it to user")
    agent = create_agent("openai:gpt-5.4", tools,
                         system_prompt="get accreos multiple ecommerce sites like amazon,bestbuy,wallmart and present it to user")
    # query ="get me best price for iphone 18 pro max"
    query =state.query
    response = await agent.ainvoke(
        {"messages": query}
    )
    # print(response["messages"][-1].content)
    state.response=response["messages"][-1].content
    return state
def direct_response_node(state: PriceComparisonState) -> PriceComparisonState:
    state.response = "Hello! How can I help you today?"
    return state
    # return {"response": f"Hello! How can I help you today?"}

# asyncio.run(price_comparison_node())