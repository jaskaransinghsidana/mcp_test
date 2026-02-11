# Agentic MCP Monorepo

This repository contains a full local stack for a **LangGraph-powered chatbot** with a modern React UI and MCP tool-calling support using **FastMCP** for both client and server.

## Monorepo structure

- `apps/api`: FastAPI backend, LangGraph agent orchestration, FastMCP client tool calls.
- `apps/web`: React + Vite chatbot UI with plan/task visualization.
- `services/mcp-server`: Sample FastMCP server exposing tools.
- `docker-compose.yml`: One-command local environment.

## Features

- LangGraph workflow with 3 graph stages:
  1. Planner node generates a tool-oriented task plan.
  2. Executor node runs tasks via MCP tools.
  3. Responder node produces a final answer from task results.
- MCP sample tool server with:
  - `weather_lookup(city)`
  - `kb_search(query)`
  - `summarize_text(text)`
- Modern chat UX showing both assistant response and execution plan.
- Environment variables centralized in `.env`.

## Environment variables

All env vars are stored in the repository root `.env`:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `API_HOST`
- `API_PORT`
- `WEB_PORT`
- `MCP_SERVER_HOST`
- `MCP_SERVER_PORT`
- `MCP_SERVER_URL`
- `BACKEND_URL`
- `VITE_API_URL`

## Run locally

```bash
docker compose up --build
```

Then open:

- UI: `http://localhost:5173`
- API health: `http://localhost:8000/health`
- MCP endpoint: `http://localhost:9001/mcp`

## Backend API

`POST /chat`

```json
{
  "message": "Plan a weather-aware day in London",
  "history": []
}
```

Returns:

- `answer`: assistant final response
- `plan`: executed tasks with status, tool name, and output

## Notes

- Replace `OPENAI_API_KEY` in `.env` before running the full agent flow.
- MCP tools are intentionally simple to act as an extendable starter template.
