# ✈️ Travel AI Assistant — LangGraph + Ollama + SerpAPI

## Project Overview

A **ReAct-based Travel AI Agent** built with LangGraph 1.2.x that can:
- 🌤️ Check **Weather** at any destination
- 🏨 Search **Hotels** with filters
- ✈️ Search **Flights** between cities
- 🗺️ Get **Maps / Directions** between locations

**LLM**: Ollama (local, e.g. `llama3.1`, `mistral`)
**Tool Execution**: SerpAPI (Google Search API)
**Orchestration**: LangGraph StateGraph with ReAct loop

---

## Architecture

```
User Input
    │
    ▼
┌─────────────────┐
│   LLM Node      │  ◄── Decides: respond OR call a tool
│  (Ollama/ReAct) │
└────────┬────────┘
         │ tool_calls detected?
         ▼
┌─────────────────────────────────────────────┐
│              Tool Execution Node             │
│  ┌──────────┐ ┌────────┐ ┌──────┐ ┌──────┐│
│  │ Weather  │ │ Hotels │ │Flights│ │ Maps ││
│  └──────────┘ └────────┘ └──────┘ └──────┘│
└────────────────────┬────────────────────────┘
                     │ results back
                     ▼
              LLM Node (again)
                     │
                     ▼ no more tool calls
                    END
```

## ReAct Loop

```
Thought → Action (tool call) → Observation (tool result) → Thought → ... → Final Answer
```

---

## Project Structure

```
travel_ai_assistant/
│
├── README.md
├── requirements.txt
├── .env.example
├── main.py                    # Entry point — run the agent
│
├── config/
│   ├── __init__.py
│   └── settings.py            # All config: model name, API keys, params
│
├── tools/
│   ├── __init__.py
│   ├── weather_tool.py        # Weather search via SerpAPI
│   ├── hotel_tool.py          # Hotel search via SerpAPI
│   ├── flight_tool.py         # Flight search via SerpAPI
│   └── maps_tool.py           # Maps/directions via SerpAPI
│
├── graph/
│   ├── __init__.py
│   ├── state.py               # AgentState TypedDict definition
│   ├── nodes.py               # llm_node + tool_node definitions
│   ├── edges.py               # Conditional routing logic
│   └── builder.py             # StateGraph construction + compilation
│
├── utils/
│   ├── __init__.py
│   └── pretty_print.py        # Colored terminal output helpers
│
└── demo.py                    # Quick demo with test queries
```

---

## Setup

### 1. Install Ollama and pull a model

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.1        # recommended — best tool calling support
# OR
ollama pull mistral
ollama pull qwen2.5
```

### 2. Install Python dependencies

```bash
cd travel_ai_assistant
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your SERPAPI_API_KEY
```

Get a free SerpAPI key at: https://serpapi.com (100 free searches/month)

### 4. Run

```bash
# Interactive mode
python main.py

# Quick demo
python demo.py
```

---

## Example Queries

```
You: I want to travel from Bangalore to Paris next week. What's the weather like there?
You: Find me hotels in Paris under $200 per night
You: Search for flights from BLR to CDG in July
You: How do I get from Eiffel Tower to Louvre Museum?
You: Plan a 3-day trip to Goa — weather, hotels, and how to get there from Bangalore
```

---

## Key Concepts Covered

| Concept | Where |
|---------|-------|
| **LLM Integration** | `graph/nodes.py` → `llm_node()` |
| **Tool Definition** | `tools/*.py` → `@tool` decorated functions |
| **Tool Execution** | `graph/nodes.py` → `tool_node()` |
| **ReAct Reasoning** | `graph/edges.py` → `should_continue()` routing |
| **Tool Messages** | `graph/state.py` → `AgentState` with `messages` |
| **Graph Building** | `graph/builder.py` → `StateGraph` with nodes/edges |