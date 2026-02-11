from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="Latest user message")
    history: List[ChatMessage] = Field(default_factory=list)


class AgentTask(BaseModel):
    id: str
    title: str
    description: str
    status: str
    tool: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    output: Optional[Any] = None


class ChatResponse(BaseModel):
    answer: str
    plan: List[AgentTask]
