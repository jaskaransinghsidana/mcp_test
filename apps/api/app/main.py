from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent import LangGraphAgent
from .models import ChatRequest, ChatResponse

app = FastAPI(title="LangGraph MCP Agent API", version="0.1.0")
agent = LangGraphAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    result = await agent.run(payload.message, payload.history)
    return ChatResponse(answer=result["answer"], plan=result["plan"])
