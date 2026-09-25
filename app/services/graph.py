from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from app.services.apify_mcp_client import price_comparison_node, direct_response_node
from app.services.state import PriceComparisonState


# class PriceComparisonState(BaseModel):
#     query: str
#     response: str

def route_intent(state: PriceComparisonState) -> str:
    # Check if input is a simple greeting
    greetings = ["hi", "hello", "hey"]
    if state.query.strip().lower() in greetings:
        return "direct_response"
    return "price_comparison"


# def price_comparison_node(state: State) -> State:
#     # Internal node with price comparison logic
#     return {"response": f"Comparing prices for: {state['user_input']}..."}

builder = StateGraph(PriceComparisonState)
builder.add_node("direct_response", direct_response_node)
builder.add_node("price_comparison", price_comparison_node)

builder.add_conditional_edges(
    START,
    route_intent,
    {
        "direct_response": "direct_response",
        "price_comparison": "price_comparison",
    }
)

builder.add_edge("direct_response", END)
builder.add_edge("price_comparison", END)

graph = builder.compile()
# Save the workflow diagram as a PNG
with open("langgraph_workflow.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())