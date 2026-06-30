from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from graph.builder import build_graph
import asyncio

app = FastAPI(title="Travel AI Assistant")
graph = build_graph()


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=open("/app/static/index.html").read())


@app.post("/chat")
async def chat(req: ChatRequest):
    result = graph.invoke({"messages": [HumanMessage(content=req.message)]})
    answer = result["messages"][-1].content
    return {"response": answer}


@app.get("/health")
async def health():
    return {"status": "ok"}
