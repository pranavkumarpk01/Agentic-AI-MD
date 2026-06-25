# ============================================================
# config/settings.py
# Centralized configuration — all tunable parameters live here
# ============================================================

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


# ── LLM (Ollama) ────────────────────────────────────────────
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Model name — must be pulled via `ollama pull <model>`
# Best tool-calling models (in order of recommendation):
#   llama3.1, llama3.2, qwen2.5, mistral
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# LLM generation parameters
OLLAMA_TEMPERATURE: float = 0.0   # 0.0 = deterministic (best for tool calling)
OLLAMA_NUM_PREDICT: int = 2048    # Max tokens to generate


# ── SerpAPI ─────────────────────────────────────────────────
SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "2dcd49ddf98f9e62112885d47abd89c97302d02f439a160962cc2c692a68b022")

if not SERPAPI_API_KEY:
    print(
        "[WARNING] SERPAPI_API_KEY is not set. "
        "Tool calls will fail. Get a free key at https://serpapi.com"
    )


# ── Agent Behaviour ──────────────────────────────────────────
# Maximum ReAct loop iterations before the graph forces termination
MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))

# Print step-by-step reasoning and tool calls to console
AGENT_VERBOSE: bool = os.getenv("AGENT_VERBOSE", "true").lower() == "true"


# ── SerpAPI Search Defaults ──────────────────────────────────
# Number of results to return per tool call
SERP_MAX_RESULTS: int = 5

# Default country/language for searches
SERP_COUNTRY: str = "us"
SERP_LANGUAGE: str = "en"


# ── System Prompt ────────────────────────────────────────────
# This is injected as the first message to guide the LLM's behaviour
SYSTEM_PROMPT: str = """You are an expert Travel AI Assistant. You help users plan trips by providing real-time information about weather, hotels, flights, and navigation.

You have access to 4 tools:
1. **weather_search** — Get current weather and forecasts for any city/destination
2. **hotel_search** — Search for hotels with filters like price, rating, location
3. **flight_search** — Search for flights between cities with dates
4. **maps_search** — Get directions, distances, and navigation between places

## How to behave:
- Always use tools to get REAL data — never make up weather, prices, or schedules
- For complex travel queries, use MULTIPLE tools in sequence (e.g., weather → hotels → flights)
- After each tool result, reason about what information you still need
- Summarize results in a clear, structured format with bullet points
- Include practical tips (best time to visit, booking advice, etc.)
- Be conversational and helpful

## ReAct Pattern:
Think step by step:
1. What does the user need?
2. Which tool(s) should I call?
3. What do the results tell me?
4. Do I need more information?
5. Give a complete, helpful final answer

Always respond in English unless the user writes in another language.
"""