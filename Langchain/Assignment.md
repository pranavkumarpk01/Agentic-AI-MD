# AI Travel Planner Agent

## Industry Assignment Guide

---

# Business Problem Statement

A travel startup wants to launch an AI-powered assistant that helps users plan trips using natural language.

The assistant should:

- Understand travel requirements
- Search for destinations
- Suggest hotels
- Estimate trip costs
- Remember recent conversations
- Generate personalized itineraries

Your task is to build this AI Agent using **LangChain** and **Ollama**.

---

# Example User Requests

1. Plan a 3-day Goa trip under ₹15,000.
2. Suggest tourist attractions in Coorg.
3. Find hotels under ₹3,000 per night.
4. Create a day-by-day itinerary.
5. What destination did I ask about previously?

---

# Learning Objectives

By completing this assignment, students should be able to:

1. Understand AI Agents and Agentic Workflows
2. Use LangChain Tools
3. Implement Window Memory
4. Integrate SQLite for persistence
5. Build Multi-Step Reasoning workflows
6. Use Ollama as a local LLM

---

# Technical Requirements & Architecture

## Architecture Flow

```text
User
  ↓
Agent
  ↓
Tool Selection
  ↓
Tool Execution
  ↓
Memory
  ↓
LLM Reasoning
  ↓
Final Response
```

---

# Mandatory Components

| Component | Requirement |
|------------|-------------|
| LLM | Ollama (Recommended: qwen3:8b) |
| Agent | LangChain ReAct Agent |
| Tools | 3 Custom Tools |
| Memory | ConversationBufferWindowMemory(k=5) |
| Database | SQLite |
| API | External API Integration |

---

# Required Tools

## Tool 1: Destination Search

### Input
Destination Name

### Output
Popular attractions and activities.

---

## Tool 2: Hotel Search

### Input
Destination + Budget

### Output
Hotels matching user criteria.

---

## Tool 3: Budget Calculator

### Input
- Hotel Cost
- Food Cost
- Transport Cost

### Output
Estimated total trip cost.

---

# Memory Requirements

Implement:

```python
ConversationBufferWindowMemory(k=5)
```

The agent should remember the last five interactions and answer follow-up questions without performing a new search.

---

# Implementation Roadmap

## Step 1
Configure Ollama and verify LLM responses.

## Step 2
Create the three required tools.

## Step 3
Build the LangChain ReAct Agent.

## Step 4
Integrate Window Memory.

## Step 5
Store conversations in SQLite.

## Step 6
Implement Multi-Step Reasoning.

## Step 7
Demonstrate memory and tool usage.

---

# Expected Multi-Step Reasoning Flow

### User Request

> Plan a Goa trip under ₹15,000.

### Agent Workflow

1. Search destination attractions
2. Search hotels within budget
3. Estimate trip cost
4. Create itinerary
5. Validate budget
6. Return final recommendation

---

# Deliverables

Students must submit:

1. Source Code
   - app.py
   - tools.py
   - memory.py
   - db.py

2. requirements.txt

3. README.md

4. 3–5 Minute Demo Video

5. Sample Conversation Screenshots

---

# Evaluation Rubric (100 Marks)

| Criteria | Marks |
|-----------|--------|
| Tool Calling | 20 |
| Memory | 20 |
| Multi-Step Reasoning | 20 |
| Ollama Integration | 10 |
| SQLite Persistence | 10 |
| Code Quality | 10 |
| Demo & Presentation | 10 |

### Total: 100 Marks

---

# Technologies Covered

- LangChain
- ReAct Agents
- Ollama
- Window Memory
- SQLite
- Tool Calling
- Multi-Step Reasoning
- Agentic AI
