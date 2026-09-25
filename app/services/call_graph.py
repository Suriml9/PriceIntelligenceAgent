# ./src/agent/webapp.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agent.graph import graph  # Import your compiled LangGraph graph

app = FastAPI()


class InvokeRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.post("/invoke")
def invoke_graph(payload: InvokeRequest):
    try:
        # Define config with thread_id for checkpointing if needed
        config = {"configurable": {"thread_id": payload.thread_id}} if payload.thread_id else {}

        # Invoke the graph with input state matching your graph schema
        result = graph.invoke({"messages": [{"role": "user", "content": payload.message}]}, config)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))