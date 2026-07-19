# LangGraph: Complete End-to-End Guide
## Mastering Stateful Agent Orchestration from Basics to Production

**Version**: 2.0 | **Last Updated**: July 2026 | **Author**: AI Notes

---

## Table of Contents
1. [Introduction & Philosophy](#introduction--philosophy)
2. [Core Concepts & Mental Models](#core-concepts--mental-models)
3. [Architecture & State Management](#architecture--state-management)
4. [Graph Construction](#graph-construction)
5. [Nodes & Edges](#nodes--edges)
6. [State Schemas & TypedDict](#state-schemas--typeddict)
7. [Conditional Routing](#conditional-routing)
8. [Checkpoints & Persistence](#checkpoints--persistence)
9. [Real-World Examples](#real-world-examples)
10. [Advanced Patterns](#advanced-patterns)
11. [Production Deployment](#production-deployment)
12. [Performance & Optimization](#performance--optimization)

---

## Introduction & Philosophy

### What is LangGraph?

LangGraph is a low-level Python orchestration framework developed by LangChain that models AI agent systems as stateful, cyclic directed graphs. Unlike linear pipelines that discard intermediate state, LangGraph maintains persistent state across graph traversals, enabling agents to loop, branch, retry, and pause in production-grade ways.

**Key Statistics (2026)**:
- Reached v1.0 in October 2025 (stable APIs)
- Focus: Stateful Orchestration era
- Philosophy: "If 2024 was RAG, 2025 was Agents, 2026 is Stateful Orchestration"
- Used by: Teams building reliable, production-grade agent systems

### Philosophy: Why Graphs?

**Linear Pipeline Problem**:
```
Input → Step 1 → Step 2 → Step 3 → Output
         (state discarded)
```
- No state persistence
- No retries or branching
- No human-in-the-loop
- Fails on complex logic

**LangGraph Solution**:
```
    ┌─► Node A ─┐
    │           ├─► Node C ◄─┐
Input ┤           │           │
    │ └─► Node B ─┘  Loop  ─►┘
    │           
    └─► Conditional Routing
    
State persists throughout entire execution
```

### Core Principles

1. **Statefulness**: Every node can read/write shared state
2. **Cyclicity**: Graphs support loops for iterative refinement
3. **Determinism**: All paths through graph are explicit and traceable
4. **Fault Tolerance**: Checkpoints enable recovery and replay
5. **Human Oversight**: Natural places for human-in-the-loop decisions

---

## Core Concepts & Mental Models

### 1. Graphs

**Definition**: A directed graph where nodes are computational steps and edges are state transitions.

**Components**:
```python
{
  "nodes": {
    "node_id": callable,  # Function to execute
    ...
  },
  "edges": [
    ("source_node", "target_node"),  # Directed edge
    ...
  ],
  "entry_point": str,     # Where to start
  "end_nodes": [str],     # Where to finish
  "state_schema": dict,   # Shared state structure
}
```

**Graph Visualization**:
```
START
  │
  ▼
┌─────────────┐
│  Process    │
│  Input      │
└────┬────────┘
     │
     ▼
┌─────────────────────────────┐
│  Route                      │
│  (Conditional branching)    │
└────┬──────────────┬─────────┘
     │              │
   route1        route2
     │              │
     ▼              ▼
┌────────────┐ ┌────────────┐
│  Agent 1   │ │  Agent 2   │
└────┬───────┘ └───┬────────┘
     │             │
     └─────┬───────┘
           │
           ▼
    ┌─────────────┐
    │  Aggregate  │
    │  Results    │
    └──────┬──────┘
           │
           ▼
        ┌─────────────┐
        │   FINISH    │
        └─────────────┘
```

### 2. State

**Definition**: A shared data structure representing the current snapshot of your application.

**State Characteristics**:
- **Shared**: All nodes can read and write
- **Typed**: Defined using TypedDict for type safety
- **Versioned**: Checkpoints preserve state at each step
- **Immutable in handlers**: Handlers return new state, not mutations

**State Evolution**:
```
Initial State: {"counter": 0, "messages": []}
    ↓
Node 1: {"counter": 1, "messages": ["msg1"]}
    ↓
Node 2: {"counter": 2, "messages": ["msg1", "msg2"]}
    ↓
Node 3: {"counter": 3, "messages": ["msg1", "msg2", "msg3"]}
```

### 3. Nodes

**Definition**: Computational units that process state and return updated state.

**Node Pattern**:
```python
def node_function(state: State) -> dict:
    """
    Takes current state → processes → returns updates
    """
    # Read from state
    value = state["field"]
    
    # Process
    result = process(value)
    
    # Return updates (partial or complete)
    return {"field": result}
```

### 4. Edges

**Definition**: Directed connections from one node to another, optionally with routing logic.

**Edge Types**:

**Simple Edge**:
```python
graph.add_edge("node_a", "node_b")
# Always go from A to B
```

**Conditional Edge**:
```python
graph.add_conditional_edges(
    "node_a",
    routing_function,
    {
        "path1": "node_b",
        "path2": "node_c",
        "path3": "node_d"
    }
)
```

### 5. Checkpoints

**Definition**: Snapshots of state at specific points enabling recovery, replay, and human review.

**Checkpoint Storage**:
```
Execution Timeline:
Start │ Checkpoint 1 │ Checkpoint 2 │ Checkpoint 3 │ End
      │ (State v1)   │ (State v2)   │ (State v3)   │
      
If error at Checkpoint 3:
→ Retry from Checkpoint 2 with State v2
→ No need to re-execute from start
```

---

## Architecture & State Management

### LangGraph System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                           │
│  (User code, business logic, workflow definitions)            │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                  GRAPH DEFINITION LAYER                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  StateGraph / CompiledGraph                            │  │
│  │  - Nodes registry                                      │  │
│  │  - Edges registry (simple & conditional)              │  │
│  │  - Entry/exit points                                   │  │
│  │  - State schema                                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                  EXECUTION ENGINE LAYER                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Scheduler  │  │  Node Exec   │  │  Edge Route  │       │
│  │  (control   │  │  Executor    │  │  Evaluator   │       │
│  │   flow)     │  │  (run nodes) │  │  (routing)   │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                  STATE MANAGEMENT LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  State Reader/Writer                                 │   │
│  │  - Immutable state updates                           │   │
│  │  - State merging                                     │   │
│  │  - Conflict resolution                              │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                  PERSISTENCE LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Checkpoint  │  │  Storage     │  │  Memory      │      │
│  │  Manager     │  │  Backend     │  │  Cleanup     │      │
│  │              │  │  (DB/File)   │  │  Scheduler   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

### State Management Deep Dive

**State Update Pattern**:

```python
# ❌ WRONG: Direct mutation (not allowed)
def node_wrong(state: State):
    state["counter"] += 1  # Mutation!
    return state

# ✅ CORRECT: Return new state updates
def node_correct(state: State) -> dict:
    return {"counter": state["counter"] + 1}
```

**State Merging Strategy**:

```
Initial State: {
  "counter": 0,
  "messages": ["a", "b"],
  "metadata": {"version": 1}
}

Node Update:
return {"counter": 5}

Merged Result:
{
  "counter": 5,        # Updated
  "messages": ["a", "b"],  # Preserved
  "metadata": {"version": 1}  # Preserved
}
```

**State Channel Merging**:

```python
# For complex merging (e.g., lists)
from langgraph.graph import DEFAULT_REDUCER, add_messages

class State(TypedDict):
    # messages is a list that appends new items
    messages: Annotated[list[Message], add_messages]
    counter: int
    metadata: dict

# When node returns {"messages": [new_msg]}
# Result: messages = old_messages + [new_msg]
```

### Execution Flow Diagram

```
┌─────────────────────────────────┐
│  Input / Initial State          │
│  {"task": "process", ...}       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Load Checkpoint (if resuming)  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Execute Current Node           │
│  - Read state                   │
│  - Run computation              │
│  - Collect results              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Save Checkpoint                │
│  - Persist state                │
│  - Record node execution        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Evaluate Edges                 │
│  - Simple: goto next node       │
│  - Conditional: run router func │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌──────────┐
│ Continue│      │  Finish? │
│ (loop)  │      └────┬─────┘
└────┬────┘           │
     │                ▼ Yes
     │           ┌─────────────┐
     │           │   Return    │
     │           │   Output    │
     │           └─────────────┘
     │
     └──────────────────────────┘ No, goto next node
```

---

## Graph Construction

### StateGraph: The Foundation

**Basic Structure**:

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

class AgentState(TypedDict):
    """Shared state schema"""
    messages: Annotated[list, "Message list"]
    counter: int
    decision: str

# Create graph
graph = StateGraph(AgentState)

# Add nodes (computational steps)
graph.add_node("entry", entry_function)
graph.add_node("process", process_function)
graph.add_node("exit", exit_function)

# Add edges (transitions)
graph.add_edge("entry", "process")
graph.add_conditional_edges("process", route_function, {
    "path_a": "exit",
    "path_b": "process"  # Can loop back
})

# Set entry/exit
graph.set_entry_point("entry")
graph.set_finish_point("exit")

# Compile
compiled_graph = graph.compile()
```

### Creating Nodes

**Simple Node**:

```python
def simple_node(state: AgentState) -> dict:
    """Process state and return updates"""
    print(f"Current counter: {state['counter']}")
    return {"counter": state["counter"] + 1}
```

**Node with Tools**:

```python
from typing import Callable
import anthropic

def tool_calling_node(state: AgentState) -> dict:
    """Node that calls tools via LLM"""
    client = anthropic.Anthropic()
    
    # Call LLM
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=[
            {
                "name": "search",
                "description": "Search for information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    }
                }
            }
        ],
        messages=state["messages"]
    )
    
    # Process response
    tool_calls = [
        block for block in response.content 
        if block.type == "tool_use"
    ]
    
    return {
        "messages": state["messages"] + [response],
        "decision": "tools_called" if tool_calls else "complete"
    }
```

**Async Node**:

```python
import asyncio

async def async_node(state: AgentState) -> dict:
    """Async node for I/O-bound operations"""
    # Async operations
    result = await fetch_data_async()
    
    return {
        "counter": state["counter"] + 1,
        "messages": state["messages"] + [result]
    }

# Use in graph
graph.add_node("async_processor", async_node)
```

### Adding Edges

**Simple Edge (Always Execute)**:

```python
# A → B (always)
graph.add_edge("node_a", "node_b")
```

**Conditional Edge (Router)**:

```python
def route_function(state: AgentState) -> str:
    """Return next node name based on state"""
    if state["counter"] > 5:
        return "path_a"
    else:
        return "path_b"

graph.add_conditional_edges(
    "current_node",
    route_function,
    {
        "path_a": "node_x",
        "path_b": "node_y"
    }
)
```

**Multi-Output Edges**:

```python
def multi_router(state: AgentState):
    """Route to multiple nodes in parallel"""
    outcomes = []
    
    if state["counter"] % 2 == 0:
        outcomes.append("even_processor")
    if state["counter"] > 10:
        outcomes.append("high_value_processor")
    
    return outcomes if outcomes else ["default"]

graph.add_conditional_edges(
    "splitter",
    multi_router
)
```

---

## Nodes & Edges

### Node Patterns

**Pattern 1: Data Transformation**

```python
def transform_node(state: AgentState) -> dict:
    """Pure data transformation"""
    messages = state["messages"]
    
    # Process
    processed = [msg.upper() for msg in messages]
    
    return {"messages": processed}
```

**Pattern 2: External API Call**

```python
def api_call_node(state: AgentState) -> dict:
    """Call external API"""
    import requests
    
    try:
        response = requests.post(
            "https://api.example.com/process",
            json={"data": state["messages"]},
            timeout=10
        )
        response.raise_for_status()
        
        return {
            "messages": state["messages"] + [response.json()],
            "counter": state["counter"] + 1
        }
    
    except requests.RequestException as e:
        return {
            "error": str(e),
            "decision": "retry"
        }
```

**Pattern 3: LLM Decision Making**

```python
from anthropic import Anthropic

def llm_decision_node(state: AgentState) -> dict:
    """Use LLM to make decisions"""
    client = Anthropic()
    
    prompt = f"""Based on the following messages, decide next action:
    {state['messages']}
    
    Return: 'continue', 'investigate', or 'stop'"""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    
    decision = response.content[0].text.strip().lower()
    
    return {
        "decision": decision,
        "messages": state["messages"] + [decision]
    }
```

**Pattern 4: Aggregation**

```python
def aggregate_node(state: AgentState) -> dict:
    """Aggregate results from multiple sources"""
    messages = state["messages"]
    
    # Extract and combine
    results = {
        "total": len(messages),
        "summary": " | ".join(messages),
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "messages": state["messages"] + [str(results)]
    }
```

**Pattern 5: Conditional Processing**

```python
def conditional_node(state: AgentState) -> dict:
    """Process based on conditions"""
    if state["counter"] < 3:
        return {
            "counter": state["counter"] + 1,
            "decision": "continue_loop"
        }
    elif state["counter"] < 10:
        return {
            "decision": "analyze"
        }
    else:
        return {
            "decision": "complete"
        }
```

### Edge Routing Patterns

**Pattern 1: Simple Binary Routing**

```python
def binary_router(state: AgentState) -> str:
    """Route to one of two paths"""
    return "success_path" if state["counter"] > 5 else "retry_path"

graph.add_conditional_edges(
    "validator",
    binary_router,
    {
        "success_path": "process_successful",
        "retry_path": "retry_process"
    }
)
```

**Pattern 2: Multi-Way Routing**

```python
def multi_router(state: AgentState) -> str:
    """Route to multiple paths based on decision"""
    decision = state["decision"]
    
    routing_map = {
        "technical": "technical_specialist",
        "billing": "billing_specialist",
        "general": "general_support",
        "urgent": "escalation_team"
    }
    
    return routing_map.get(decision, "general_support")
```

**Pattern 3: Parallel Routing**

```python
from langgraph.graph import Send

def parallel_router(state: AgentState):
    """Send to multiple nodes in parallel"""
    nodes_to_execute = []
    
    if "analysis_needed" in state.get("tags", []):
        nodes_to_execute.append(Send("analyzer", state))
    
    if "report_needed" in state.get("tags", []):
        nodes_to_execute.append(Send("reporter", state))
    
    if "alert_needed" in state.get("tags", []):
        nodes_to_execute.append(Send("alerter", state))
    
    return nodes_to_execute or [Send("default_handler", state)]
```

**Pattern 4: Conditional Retry Logic**

```python
def retry_router(state: AgentState) -> str:
    """Route based on retry count"""
    retry_count = state.get("retry_count", 0)
    max_retries = 3
    
    if retry_count < max_retries and state.get("error"):
        return "retry"
    elif retry_count >= max_retries:
        return "error_handler"
    else:
        return "success_handler"
```

**Pattern 5: Tool-Based Routing**

```python
from langgraph.prebuilt import tools_condition

# Built-in router for tool use
# Routes to 'tools' node if LLM called tools, else 'end'
graph.add_conditional_edges(
    "agent",
    tools_condition,  # Built-in from LangGraph
    {
        "tools": "tools_node",
        "end": "__end__"
    }
)
```

---

## State Schemas & TypedDict

### Basic State Definition

```python
from typing import TypedDict, Annotated, Literal

class SimpleState(TypedDict):
    """Minimal state schema"""
    input: str
    output: str
    counter: int
```

### Advanced State with Annotations

```python
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import DEFAULT_REDUCER, add_messages
from anthropic import HumanMessage, AIMessage

class AdvancedState(TypedDict):
    """Rich state with semantic information"""
    # Messages with custom reducer (append semantics)
    messages: Annotated[
        Sequence,
        add_messages  # Automatically merges new messages
    ]
    
    # Metadata
    user_id: str
    session_id: str
    start_time: float
    
    # Results and tracking
    counter: Annotated[
        int,
        DEFAULT_REDUCER  # Keeps latest value
    ]
    
    # Analysis results
    analysis: Annotated[
        dict,
        "Merges new analysis results with existing"
    ]
    
    # Decision tracking
    decisions: Annotated[
        list[str],
        "Tracks all decisions made"
    ]
```

### State with Custom Reducers

```python
from typing import Annotated
from langgraph.graph.message import add_messages

def custom_reducer(left, right):
    """Custom merge logic"""
    if isinstance(left, list) and isinstance(right, list):
        # Remove duplicates and sort
        return sorted(list(set(left + right)))
    return right

class CustomReducerState(TypedDict):
    # Keeps last 5 items
    recent_items: Annotated[
        list[str],
        lambda left, right: (left + right)[-5:] if left else right
    ]
    
    # Merges dictionaries deeply
    config: Annotated[
        dict,
        lambda left, right: {**left, **right}
    ]
    
    # Custom list merge
    tags: Annotated[
        list[str],
        custom_reducer
    ]
```

### Nested State Structures

```python
from typing import TypedDict, Sequence
from dataclasses import dataclass

@dataclass
class ProcessResult:
    status: str
    data: dict
    timestamp: float

class NestedState(TypedDict):
    """State with nested structures"""
    # Nested object
    result: ProcessResult
    
    # Nested list of objects
    results: Sequence[ProcessResult]
    
    # Nested dict
    metadata: dict[str, any]
    
    # Deeply nested
    config: dict[str, dict[str, any]]
```

---

## Conditional Routing

### Basic Conditional Routing

```python
def simple_router(state: AgentState) -> Literal["path_a", "path_b"]:
    """Simple if-else routing"""
    if state["counter"] > 10:
        return "path_a"
    else:
        return "path_b"

graph.add_conditional_edges(
    "decision_node",
    simple_router,
    {
        "path_a": "high_value_handler",
        "path_b": "standard_handler"
    }
)
```

### Multi-Condition Routing

```python
def complex_router(state: AgentState) -> str:
    """Multiple conditions"""
    counter = state["counter"]
    decision = state.get("decision", "none")
    
    # Priority-based routing
    if counter > 100:
        return "critical_path"
    elif decision == "escalate":
        return "escalation_team"
    elif decision == "investigate":
        return "investigation_team"
    elif counter > 50:
        return "priority_path"
    else:
        return "standard_path"

graph.add_conditional_edges(
    "router",
    complex_router,
    {
        "critical_path": "critical_handler",
        "escalation_team": "escalate_node",
        "investigation_team": "investigate_node",
        "priority_path": "priority_handler",
        "standard_path": "standard_handler"
    }
)
```

### Loop-Back Routing

```python
def iteration_router(state: AgentState) -> str:
    """Determine if loop should continue"""
    iteration_count = state.get("iteration_count", 0)
    is_satisfied = state.get("is_satisfied", False)
    max_iterations = 5
    
    if is_satisfied:
        return "finish"
    elif iteration_count < max_iterations:
        return "process"  # Loop back
    else:
        return "max_iterations_reached"

graph.add_conditional_edges(
    "check_condition",
    iteration_router,
    {
        "process": "main_processor",  # Can point back to process
        "finish": "finalize",
        "max_iterations_reached": "error_handler"
    }
)
```

### Dynamic Routing

```python
from langgraph.graph import Send

def dynamic_router(state: AgentState):
    """Dynamically send to multiple nodes"""
    
    # Determine which processors to activate
    processors = []
    
    for item in state.get("items", []):
        if item["type"] == "A":
            processors.append(Send("process_type_a", {"item": item}))
        elif item["type"] == "B":
            processors.append(Send("process_type_b", {"item": item}))
    
    return processors if processors else [Send("default", state)]

# Usage
graph.add_conditional_edges(
    "distributor",
    dynamic_router
)
```

### Tool-Based Routing

```python
def should_use_tools(state: AgentState) -> Literal["tools", "end"]:
    """Decide if tools are needed"""
    messages = state["messages"]
    
    # Check if last message has tool calls
    last_message = messages[-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        return "end"

graph.add_conditional_edges(
    "agent",
    should_use_tools,
    {
        "tools": "tools_node",
        "end": "__end__"
    }
)
```

---

## Checkpoints & Persistence

### Checkpoint Architecture

```
Execution with Checkpoints:

Step 1: Initial State
  │
  ├─► Save Checkpoint 1 ─► Storage
  │
  ▼
Step 2: Node Execution
  │
  ├─► Save Checkpoint 2 ─► Storage
  │
  ▼
Step 3: Node Execution
  │
  ├─► Save Checkpoint 3 ─► Storage
  │
  ▼
Step 4: Error Occurs ✗
  │
  ├─► Retry from Checkpoint 3
  │
  ▼
Step 3 Redux: Re-execute
```

### Memory Checkpoints

```python
from langgraph.checkpoint.memory import MemorySaver

# Simple in-memory checkpoints (development)
checkpoint_storage = MemorySaver()

graph = StateGraph(AgentState)
# ... add nodes and edges ...

compiled_graph = graph.compile(
    checkpointer=checkpoint_storage
)

# Execute with checkpoints
result = compiled_graph.invoke(
    initial_state,
    config={"configurable": {"thread_id": "session_123"}}
)

# Resume from checkpoint
result = compiled_graph.invoke(
    None,  # Use checkpoint state
    config={"configurable": {"thread_id": "session_123"}}
)
```

### Database Checkpoints

```python
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

# PostgreSQL checkpoints (production)
connection_string = "postgresql://user:password@localhost/langgraph"

with psycopg.connect(connection_string) as conn:
    checkpoint_storage = PostgresSaver(conn)
    
    graph = StateGraph(AgentState)
    # ... add nodes and edges ...
    
    compiled_graph = graph.compile(
        checkpointer=checkpoint_storage
    )
    
    # Execute
    result = compiled_graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": "user_456"}}
    )
    
    # Resume
    result = compiled_graph.invoke(
        None,
        config={"configurable": {"thread_id": "user_456"}}
    )
```

### SQLite Checkpoints

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# SQLite checkpoints (lightweight, local)
sqlite_path = "./langraph_checkpoints.db"

with SqliteSaver.from_conn_string(sqlite_path) as checkpointer:
    compiled_graph = graph.compile(checkpointer=checkpointer)
    
    # Execute with checkpoint
    result = compiled_graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": "session_xyz"}}
    )
```

### Checkpoint Management

**Get Checkpoint History**:

```python
def get_execution_history(compiled_graph, thread_id: str):
    """Retrieve execution history"""
    # Get all checkpoints for thread
    checkpoints = compiled_graph.get_state_history(
        {"configurable": {"thread_id": thread_id}}
    )
    
    for checkpoint in checkpoints:
        print(f"Step: {checkpoint['step']}")
        print(f"State: {checkpoint['state']}")
        print(f"Timestamp: {checkpoint['timestamp']}")
```

**Replay from Checkpoint**:

```python
def replay_from_checkpoint(compiled_graph, thread_id: str, step: int):
    """Replay execution from specific checkpoint"""
    state_at_step = compiled_graph.get_state_history(
        {"configurable": {"thread_id": thread_id}}
    )[step]
    
    # Resume from checkpoint
    result = compiled_graph.invoke(
        None,
        config={
            "configurable": {"thread_id": thread_id},
            "checkpoint_step": step
        }
    )
    
    return result
```

---

## Real-World Examples

### Example 1: Multi-Agent Research System

**Scenario**: Autonomous research system that gathers, analyzes, and summarizes information.

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END, DEFAULT_REDUCER, add_messages
from langgraph.checkpoint.memory import MemorySaver
from anthropic import Anthropic, HumanMessage
import json

# State definition
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    research_query: str
    gathered_data: Annotated[list, lambda x, y: x + y if x else y]
    analysis: dict
    final_report: str
    iteration_count: int

# Initialize LLM
client = Anthropic()

# Node 1: Researcher
def researcher_node(state: ResearchState) -> dict:
    """Gather research data"""
    messages = state["messages"] + [
        HumanMessage(
            content=f"""You are a research expert. 
            Research the following query and provide findings:
            {state['research_query']}
            
            Format your response as a list of key findings."""
        )
    ]
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": m.type, "content": m.content} 
                  for m in messages]
    )
    
    findings = response.content[0].text
    
    return {
        "messages": state["messages"] + [
            HumanMessage(content=findings)
        ],
        "gathered_data": [findings]
    }

# Node 2: Analyzer
def analyzer_node(state: ResearchState) -> dict:
    """Analyze gathered data"""
    data = "\n".join(state["gathered_data"])
    
    analysis_prompt = f"""Analyze the following research data and extract key patterns:
    
    {data}
    
    Provide analysis in JSON format with: patterns, insights, implications"""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": analysis_prompt}]
    )
    
    try:
        analysis = json.loads(response.content[0].text)
    except:
        analysis = {"raw": response.content[0].text}
    
    return {
        "analysis": analysis,
        "iteration_count": state["iteration_count"] + 1
    }

# Node 3: Quality Check
def quality_check_node(state: ResearchState) -> dict:
    """Determine if analysis is sufficient"""
    analysis = state["analysis"]
    
    # Check if analysis is comprehensive
    required_keys = ["patterns", "insights", "implications"]
    is_complete = all(key in analysis for key in required_keys)
    
    if is_complete and state["iteration_count"] >= 2:
        return {"decision": "complete"}
    else:
        return {"decision": "refine"}

# Node 4: Report Generation
def report_node(state: ResearchState) -> dict:
    """Generate final report"""
    data = "\n".join(state["gathered_data"])
    analysis = json.dumps(state["analysis"], indent=2)
    
    report_prompt = f"""Create a comprehensive research report based on:
    
    Research Query: {state['research_query']}
    
    Gathered Data:
    {data}
    
    Analysis:
    {analysis}
    
    Format as a professional report with sections."""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": report_prompt}]
    )
    
    return {
        "final_report": response.content[0].text
    }

# Build graph
graph = StateGraph(ResearchState)

# Add nodes
graph.add_node("researcher", researcher_node)
graph.add_node("analyzer", analyzer_node)
graph.add_node("quality_check", quality_check_node)
graph.add_node("reporter", report_node)

# Add edges
graph.add_edge(START, "researcher")
graph.add_edge("researcher", "analyzer")
graph.add_edge("analyzer", "quality_check")

# Conditional routing
def quality_router(state: ResearchState) -> str:
    return "reporter" if state.get("decision") == "complete" else "researcher"

graph.add_conditional_edges(
    "quality_check",
    quality_router,
    {
        "reporter": "reporter",
        "researcher": "researcher"
    }
)

graph.add_edge("reporter", END)

# Compile
checkpointer = MemorySaver()
compiled_graph = graph.compile(checkpointer=checkpointer)

# Execute
initial_state = {
    "messages": [],
    "research_query": "What are the latest breakthroughs in quantum computing?",
    "gathered_data": [],
    "analysis": {},
    "final_report": "",
    "iteration_count": 0
}

result = compiled_graph.invoke(
    initial_state,
    config={"configurable": {"thread_id": "research_session_1"}}
)

print(result["final_report"])
```

### Example 2: Customer Support Routing System

**Scenario**: Route support tickets to appropriate handlers based on analysis.

```python
from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph import Send
from anthropic import Anthropic

class SupportTicket(TypedDict):
    ticket_id: str
    message: str
    category: str
    priority: str
    assigned_to: str
    resolution: str

class SupportState(TypedDict):
    tickets: list[SupportTicket]
    current_ticket: SupportTicket
    analysis_result: dict
    resolution_attempts: int

client = Anthropic()

# Node 1: Classify ticket
def classify_ticket_node(state: SupportState) -> dict:
    """Classify ticket by category and priority"""
    ticket = state["current_ticket"]
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Classify this support ticket:
            
            Message: {ticket['message']}
            
            Determine:
            1. Category (technical/billing/feature/other)
            2. Priority (low/medium/high/critical)
            
            Respond in JSON format."""
        }]
    )
    
    import json
    classification = json.loads(response.content[0].text)
    
    return {
        "current_ticket": {
            **ticket,
            "category": classification.get("category", "other"),
            "priority": classification.get("priority", "medium")
        }
    }

# Node 2: Technical handler
def technical_handler_node(state: SupportState) -> dict:
    """Handle technical support tickets"""
    ticket = state["current_ticket"]
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Solve this technical issue:
            {ticket['message']}
            
            Provide step-by-step solution."""
        }]
    )
    
    return {
        "current_ticket": {
            **ticket,
            "assigned_to": "technical_team",
            "resolution": response.content[0].text
        }
    }

# Node 3: Billing handler
def billing_handler_node(state: SupportState) -> dict:
    """Handle billing inquiries"""
    ticket = state["current_ticket"]
    
    # In real scenario, check billing system
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Resolve this billing issue:
            {ticket['message']}
            
            Provide resolution."""
        }]
    )
    
    return {
        "current_ticket": {
            **ticket,
            "assigned_to": "billing_team",
            "resolution": response.content[0].text
        }
    }

# Node 4: Feature request handler
def feature_handler_node(state: SupportState) -> dict:
    """Handle feature requests"""
    ticket = state["current_ticket"]
    
    return {
        "current_ticket": {
            **ticket,
            "assigned_to": "product_team",
            "resolution": "Feature request logged and will be reviewed in next sprint."
        }
    }

# Node 5: Escalation
def escalation_node(state: SupportState) -> dict:
    """Escalate urgent issues"""
    ticket = state["current_ticket"]
    
    return {
        "current_ticket": {
            **ticket,
            "assigned_to": "escalation_team",
            "resolution": "Ticket escalated to senior team for immediate attention."
        }
    }

# Build graph
graph = StateGraph(SupportState)

# Add nodes
graph.add_node("classify", classify_ticket_node)
graph.add_node("technical", technical_handler_node)
graph.add_node("billing", billing_handler_node)
graph.add_node("feature", feature_handler_node)
graph.add_node("escalate", escalation_node)

# Add edges
graph.add_edge(START, "classify")

# Router after classification
def route_by_category(state: SupportState) -> str:
    ticket = state["current_ticket"]
    
    if ticket["priority"] == "critical":
        return "escalate"
    
    category_map = {
        "technical": "technical",
        "billing": "billing",
        "feature": "feature"
    }
    
    return category_map.get(ticket["category"], "escalate")

graph.add_conditional_edges(
    "classify",
    route_by_category,
    {
        "technical": "technical",
        "billing": "billing",
        "feature": "feature",
        "escalate": "escalate"
    }
)

# All handlers end
graph.add_edge("technical", END)
graph.add_edge("billing", END)
graph.add_edge("feature", END)
graph.add_edge("escalate", END)

# Compile
compiled_graph = graph.compile()

# Execute
ticket = {
    "ticket_id": "TKT001",
    "message": "My database connection is timing out",
    "category": "",
    "priority": "",
    "assigned_to": "",
    "resolution": ""
}

result = compiled_graph.invoke({
    "tickets": [ticket],
    "current_ticket": ticket,
    "analysis_result": {},
    "resolution_attempts": 0
})

print(f"Assigned to: {result['current_ticket']['assigned_to']}")
print(f"Resolution: {result['current_ticket']['resolution']}")
```

### Example 3: Document Processing Pipeline

**Scenario**: Process documents through extraction, validation, and storage stages.

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END, Send
import json

class DocumentState(TypedDict):
    documents: list[dict]
    extracted_data: list[dict]
    validated_data: list[dict]
    errors: list[str]
    status: str

# Node 1: Extract
def extract_node(state: DocumentState) -> dict:
    """Extract data from documents"""
    extracted = []
    
    for doc in state["documents"]:
        # Simulate extraction
        extracted.append({
            "doc_id": doc["id"],
            "text": doc["content"],
            "extracted": True
        })
    
    return {"extracted_data": extracted}

# Node 2: Validate
def validate_node(state: DocumentState) -> dict:
    """Validate extracted data"""
    validated = []
    errors = []
    
    for item in state["extracted_data"]:
        if item.get("text"):  # Simple validation
            validated.append(item)
        else:
            errors.append(f"Invalid document: {item['doc_id']}")
    
    return {
        "validated_data": validated,
        "errors": errors
    }

# Node 3: Store
def store_node(state: DocumentState) -> dict:
    """Store validated data"""
    # Simulate storage
    stored_count = len(state["validated_data"])
    
    return {
        "status": f"Stored {stored_count} documents"
    }

# Build graph
graph = StateGraph(DocumentState)

graph.add_node("extract", extract_node)
graph.add_node("validate", validate_node)
graph.add_node("store", store_node)

graph.add_edge(START, "extract")
graph.add_edge("extract", "validate")
graph.add_edge("validate", "store")
graph.add_edge("store", END)

# Compile and execute
compiled_graph = graph.compile()

initial_state = {
    "documents": [
        {"id": "1", "content": "Document 1 content"},
        {"id": "2", "content": "Document 2 content"}
    ],
    "extracted_data": [],
    "validated_data": [],
    "errors": [],
    "status": ""
}

result = compiled_graph.invoke(initial_state)
print(result["status"])
```

---

## Advanced Patterns

### Pattern 1: Stateful Persistence Across Runs

```python
from langgraph.checkpoint.postgres import PostgresSaver

def create_persistent_workflow():
    """Create workflow with persistent state"""
    checkpoint = PostgresSaver(connection_string)
    
    graph = StateGraph(MyState)
    # ... build graph ...
    
    compiled = graph.compile(checkpointer=checkpoint)
    
    # First run
    result1 = compiled.invoke(
        initial_state,
        config={"configurable": {"thread_id": "user_123"}}
    )
    
    # Later - continue from checkpoint
    result2 = compiled.invoke(
        {"new_input": "data"},
        config={"configurable": {"thread_id": "user_123"}}
    )
```

### Pattern 2: Parallel Processing with Aggregation

```python
from langgraph.graph import Send

class AggregationState(TypedDict):
    items: list[str]
    results: Annotated[list, lambda x, y: x + y if x else y]
    final_result: str

def process_items_parallel(state: AggregationState):
    """Send each item to processor in parallel"""
    return [
        Send("process_item", {"item": item})
        for item in state["items"]
    ]

def process_item(state: AggregationState) -> dict:
    """Process single item"""
    processed = state["item"].upper()
    return {"results": [processed]}

def aggregate(state: AggregationState) -> dict:
    """Aggregate results"""
    final = " | ".join(state["results"])
    return {"final_result": final}

# Build graph
graph = StateGraph(AggregationState)
graph.add_node("distributor", process_items_parallel)
graph.add_node("process_item", process_item)
graph.add_node("aggregate", aggregate)

graph.add_edge(START, "distributor")
graph.add_conditional_edges("distributor", lambda x: ["aggregate"])
graph.add_edge("aggregate", END)
```

### Pattern 3: Dynamic State Updates

```python
class DynamicState(TypedDict):
    query: str
    context: dict
    iterations: int

def dynamic_processor(state: DynamicState) -> dict:
    """Dynamically update state"""
    new_context = {
        **state["context"],
        "processed_at": datetime.now().isoformat(),
        "iteration": state["iterations"]
    }
    
    return {
        "context": new_context,
        "iterations": state["iterations"] + 1
    }
```

### Pattern 4: Error Recovery with Fallback

```python
def main_processor(state: State) -> dict:
    """Try main processing"""
    try:
        result = risky_operation()
        return {"result": result, "error": None}
    except Exception as e:
        return {"error": str(e)}

def router_with_fallback(state: State) -> str:
    """Route to fallback if error"""
    if state.get("error"):
        return "fallback"
    else:
        return "success"

def fallback_processor(state: State) -> dict:
    """Fallback processing"""
    return {"result": "fallback_result"}

graph.add_conditional_edges(
    "main",
    router_with_fallback,
    {"success": END, "fallback": "fallback"}
)
graph.add_edge("fallback", END)
```

---

## Production Deployment

### 1. Docker Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV LANGGRAPH_DB_URL=postgresql://user:pass@db:5432/langgraph

CMD ["python", "-m", "langgraph", "api", "app:compiled_graph"]
```

### 2. API Server

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver

app = FastAPI()

# Setup checkpointing
checkpointer = PostgresSaver(os.getenv("DB_URL"))

# Build and compile graph
graph = StateGraph(State)
# ... add nodes and edges ...
compiled_graph = graph.compile(checkpointer=checkpointer)

class InvokeRequest(BaseModel):
    input: dict
    thread_id: str

@app.post("/invoke")
async def invoke(request: InvokeRequest):
    """Execute graph with checkpoint"""
    try:
        result = compiled_graph.invoke(
            request.input,
            config={"configurable": {"thread_id": request.thread_id}}
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{thread_id}")
async def get_history(thread_id: str):
    """Get execution history"""
    history = compiled_graph.get_state_history(
        {"configurable": {"thread_id": thread_id}}
    )
    return {"history": list(history)}
```

### 3. Monitoring & Observability

```python
import logging
from datetime import datetime
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def monitor_execution(func):
    """Monitor node execution"""
    @wraps(func)
    def wrapper(state):
        start_time = datetime.now()
        logger.info(f"Starting {func.__name__}")
        
        try:
            result = func(state)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Completed {func.__name__} in {duration}s")
            return result
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            raise
    
    return wrapper

@monitor_execution
def my_node(state):
    # Implementation
    pass
```

---

## Performance & Optimization

### 1. Efficient State Management

```python
# ✅ Good: Only update necessary fields
def efficient_node(state: State) -> dict:
    return {"field_to_update": new_value}  # Partial update

# ❌ Bad: Return entire state
def inefficient_node(state: State) -> dict:
    new_state = state.copy()
    new_state["field"] = value
    return new_state  # Unnecessary full copy
```

### 2. Parallel Execution

```python
from langgraph.graph import Send

def parallel_processor(state: State):
    """Process items in parallel"""
    return [
        Send("worker", {"item": item, "id": i})
        for i, item in enumerate(state["items"])
    ]

# Workers execute in parallel, results aggregated
```

### 3. Checkpoint Optimization

```python
# Only save important checkpoints
graph = StateGraph(State)

# Critical checkpoint
graph.add_node("critical", critical_node)

# Can skip non-critical checkpoints
graph.add_node("auxiliary", auxiliary_node)

# Save after critical steps
compiled = graph.compile(checkpointer=checkpointer)
```

---

## Summary & Quick Reference

### Graph Building Steps

1. **Define State** - TypedDict with your schema
2. **Create StateGraph** - Pass State class
3. **Add Nodes** - Computational functions
4. **Add Edges** - Connections between nodes
5. **Set Entry/Exit** - Start and end points
6. **Add Routing** - Conditional logic
7. **Compile** - With optional checkpointer
8. **Invoke** - Run with initial state

### Key Differences: LangGraph vs CrewAI

| Aspect | LangGraph | CrewAI |
|--------|-----------|---------|
| Model | State graphs | Agent teams |
| State | Explicit TypedDict | Implicit |
| Flow | Deterministic routing | Autonomous agents |
| Complexity | Low-level control | High-level abstractions |
| Use Case | Stateful workflows | Multi-agent coordination |
| Learning Curve | Steeper | Easier |

---

## References & Resources

- [LangGraph Official Docs](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangChain Blog](https://www.langchain.com/langgraph)
- [State Management Guide](https://deepwiki.com/langchain-ai/langgraph-101/3.1-state-management)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)