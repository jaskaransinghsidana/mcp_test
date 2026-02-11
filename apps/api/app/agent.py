from __future__ import annotations

import json
import os
import uuid
from typing import Annotated, Any, Dict, List, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from .mcp_client import MCPToolClient
from .models import AgentTask, ChatMessage


class AgentState(TypedDict):
    query: str
    history: List[ChatMessage]
    plan: List[Dict[str, Any]]
    task_results: List[Dict[str, Any]]
    answer: str


SYSTEM_PLANNER_PROMPT = """You are an agentic planner for a LangGraph assistant.
Return ONLY valid JSON as a list of tasks.
Each task MUST include: title, description, tool, and tool_input.
Available tools:
- weather_lookup {\"city\": str}
- kb_search {\"query\": str}
- summarize_text {\"text\": str}
At least one task should be included.
"""

SYSTEM_RESPONDER_PROMPT = """You are a helpful AI assistant.
Use the provided plan and task results to answer clearly.
Mention key findings and call out limitations.
"""


class LangGraphAgent:
    def __init__(self) -> None:
        self.model = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
        )
        self.mcp_client = MCPToolClient(os.getenv("MCP_SERVER_URL", "http://localhost:9001/mcp"))
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("plan", self._create_plan)
        workflow.add_node("execute", self._execute_tasks)
        workflow.add_node("respond", self._build_response)
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "respond")
        workflow.add_edge("respond", END)
        return workflow.compile()

    async def _create_plan(self, state: AgentState) -> AgentState:
        history_text = "\n".join([f"{m.role}: {m.content}" for m in state["history"][-6:]])
        prompt = (
            f"User question: {state['query']}\n"
            f"Recent history:\n{history_text or 'No history'}\n"
            "Create a concise tool-oriented task plan."
        )
        response = await self.model.ainvoke([SystemMessage(content=SYSTEM_PLANNER_PROMPT), HumanMessage(content=prompt)])

        raw = response.content if isinstance(response.content, str) else str(response.content)
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, list):
                raise ValueError("Plan must be a list")
        except Exception:
            parsed = [
                {
                    "title": "Knowledge lookup",
                    "description": "Search reference material related to the user request",
                    "tool": "kb_search",
                    "tool_input": {"query": state["query"]},
                }
            ]

        plan = []
        for item in parsed:
            plan.append(
                {
                    "id": str(uuid.uuid4()),
                    "title": item.get("title", "Untitled task"),
                    "description": item.get("description", "No description"),
                    "status": "pending",
                    "tool": item.get("tool"),
                    "tool_input": item.get("tool_input", {}),
                }
            )

        return {**state, "plan": plan}

    async def _execute_tasks(self, state: AgentState) -> AgentState:
        results: List[Dict[str, Any]] = []
        plan = []

        for task in state["plan"]:
            mutable = {**task, "status": "running"}
            tool = mutable.get("tool")
            try:
                output = await self.mcp_client.call_tool(tool, mutable.get("tool_input", {}))
                mutable["status"] = "completed"
                mutable["output"] = output
                results.append({"task_id": mutable["id"], "tool": tool, "output": output})
            except Exception as exc:
                mutable["status"] = "failed"
                mutable["output"] = {"error": str(exc)}
                results.append({"task_id": mutable["id"], "tool": tool, "output": {"error": str(exc)}})
            plan.append(mutable)

        return {**state, "plan": plan, "task_results": results}

    async def _build_response(self, state: AgentState) -> AgentState:
        plan_json = json.dumps(state["plan"], indent=2)
        results_json = json.dumps(state["task_results"], indent=2)

        prompt = (
            f"User query: {state['query']}\n\n"
            f"Plan:\n{plan_json}\n\n"
            f"Task results:\n{results_json}\n\n"
            "Generate a concise final answer with bullet points when useful."
        )

        response = await self.model.ainvoke([SystemMessage(content=SYSTEM_RESPONDER_PROMPT), HumanMessage(content=prompt)])
        answer = response.content if isinstance(response.content, str) else str(response.content)
        return {**state, "answer": answer}

    async def run(self, query: str, history: List[ChatMessage]) -> Dict[str, Any]:
        initial: AgentState = {
            "query": query,
            "history": history,
            "plan": [],
            "task_results": [],
            "answer": "",
        }

        output = await self.graph.ainvoke(initial)
        tasks = [AgentTask(**task) for task in output["plan"]]
        return {"answer": output["answer"], "plan": tasks}
