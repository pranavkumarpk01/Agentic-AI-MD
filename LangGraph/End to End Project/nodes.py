import json
import ollama

from state import ResearchState
from tools import search_web
from memory_store import load_user_memory, save_user_memory

MODEL = "llama3.2:3b"


# ---------------------------------------------------------------------------
# Helper: clean up LLM output before JSON parsing
# ---------------------------------------------------------------------------

def _parse_json(text: str):
    """Strip markdown fences and parse JSON from LLM output."""
    text = text.strip()
    if "```" in text:
        # Pull out the content between ``` blocks
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except Exception:
                continue
    return json.loads(text)


# ---------------------------------------------------------------------------
# Node 1 — Load Memory
# ---------------------------------------------------------------------------

def load_memory_node(state: ResearchState) -> dict:
    """Load user's past knowledge from Redis before anything else."""
    print("\n[Node] LOAD MEMORY")
    facts = load_user_memory(state["user_id"])
    print(f"  Loaded {len(facts)} facts")
    return {"past_memory": facts}


# ---------------------------------------------------------------------------
# Node 2 — LLM Decision: Search Needed?
# ---------------------------------------------------------------------------

def decide_search_node(state: ResearchState) -> dict:
    """
    LLM looks at the query + existing memory and decides
    whether a web search is actually needed.
    """
    print("\n[Node] LLM DECISION — Need web search?")

    memory_lines = "\n".join(f"- {f}" for f in state.get("past_memory", []))

    prompt = f"""You are a research assistant deciding whether to search the web.

User query: "{state['query']}"

Facts already in memory:
{memory_lines if memory_lines else "- (none)"}

Should I search the web to answer this accurately?
- If memory already covers it well → no search needed
- If query needs current/specific/technical info → search needed

Reply ONLY with valid JSON (no markdown, no extra text):
{{"needs_search": true, "reason": "one sentence explaining your decision"}}"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response["message"]["content"]
    print(f"  LLM raw response: {content[:120]}")

    try:
        result = _parse_json(content)
        needs_search = bool(result.get("needs_search", True))
        reason = result.get("reason", "")
    except Exception:
        needs_search = True
        reason = "Could not parse LLM response — defaulting to search"

    print(f"  Decision: needs_search={needs_search}")

    return {
        "needs_search": needs_search,
        "messages": [
            {
                "role": "assistant",
                "content": f"🤔 **Search decision**: {'Web search needed' if needs_search else 'Memory is sufficient'} — {reason}",
            }
        ],
    }


# ---------------------------------------------------------------------------
# Node 3 — Tool Call: SerpAPI Web Search
# ---------------------------------------------------------------------------

def search_web_node(state: ResearchState) -> dict:
    """Call SerpAPI to search the web. This is our tool call node."""
    print("\n[Node] SEARCH WEB — SerpAPI tool call")

    results = search_web(state["query"])
    print(f"  Got {len(results)} results")

    return {
        "search_results": results,
        "messages": [
            {
                "role": "tool",
                "content": f"🔍 SerpAPI returned {len(results)} results for: \"{state['query']}\"",
            }
        ],
    }


# ---------------------------------------------------------------------------
# Node 4 — LLM Summarize
# ---------------------------------------------------------------------------

def summarize_node(state: ResearchState) -> dict:
    """LLM synthesizes search results + memory into a clear response."""
    print("\n[Node] LLM SUMMARIZE")

    search_ctx = "\n\n".join(state.get("search_results", []))
    memory_ctx = "\n".join(f"- {f}" for f in state.get("past_memory", []))

    prompt = f"""You are a helpful research assistant.

Query: "{state['query']}"

Web search results:
{search_ctx if search_ctx else "(no web search performed — answering from memory)"}

Previously known facts:
{memory_ctx if memory_ctx else "(none)"}

Write a clear, informative, well-structured response. Be thorough but concise."""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    summary = response["message"]["content"]
    print(f"  Summary generated ({len(summary)} chars)")

    return {
        "summary": summary,
        "messages": [{"role": "assistant", "content": summary}],
    }


# ---------------------------------------------------------------------------
# Node 5 — LLM: What Should We Remember?
# ---------------------------------------------------------------------------

def extract_memory_node(state: ResearchState) -> dict:
    """
    LLM reads the summary and decides which facts are worth
    storing in long-term memory. This is the 'smart memory' node.
    """
    print("\n[Node] LLM EXTRACT MEMORY — What's worth saving?")

    prompt = f"""You just researched: "{state['query']}"

Summary of findings:
{state['summary']}

Which facts from this research are genuinely useful to remember for FUTURE queries?
Be SELECTIVE — only save facts that are:
- Reusable across different future questions
- Not too query-specific or trivial
- Factual and worth knowing long-term

Reply ONLY with a JSON array of strings (no markdown, no extra text):
["fact one", "fact two", ...]

If nothing is worth saving, return: []"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response["message"]["content"]
    print(f"  LLM raw response: {content[:200]}")

    try:
        facts = _parse_json(content)
        if not isinstance(facts, list):
            facts = []
        facts = [str(f).strip() for f in facts if f]
    except Exception:
        facts = []

    print(f"  LLM chose to remember {len(facts)} facts: {facts}")

    return {
        "memory_facts": facts,
        "messages": [
            {
                "role": "assistant",
                "content": f"💡 LLM selected **{len(facts)} fact(s)** to remember"
                + (f":\n" + "\n".join(f"• {f}" for f in facts) if facts else " (nothing worth saving)"),
            }
        ],
    }


# ---------------------------------------------------------------------------
# Node 6 — Human Approval (graph pauses BEFORE this via interrupt_before)
# ---------------------------------------------------------------------------

def human_approval_node(state: ResearchState) -> dict:
    """
    The graph interrupts BEFORE this node runs (see graph.py).
    By the time this runs, human_approved has been set via the API.
    """
    print("\n[Node] HUMAN APPROVAL — decision already recorded in state")
    return {}


# ---------------------------------------------------------------------------
# Node 7 — Save to Redis Memory
# ---------------------------------------------------------------------------

def save_memory_node(state: ResearchState) -> dict:
    """Save LLM-selected facts to Redis (only if human approved)."""
    print("\n[Node] SAVE MEMORY TO REDIS")

    if state.get("human_approved") and state.get("memory_facts"):
        save_user_memory(state["user_id"], state["memory_facts"])
        return {
            "messages": [
                {
                    "role": "system",
                    "content": f"✅ Saved {len(state['memory_facts'])} fact(s) to Redis memory",
                }
            ]
        }

    print("  Skipped — not approved or no facts")
    return {}


# ---------------------------------------------------------------------------
# Node 8 — Save to DB (INTENTIONALLY BROKEN for checkpoint demo)
# ---------------------------------------------------------------------------

def save_to_db_node(state: ResearchState) -> dict:
    """
    This node is INTENTIONALLY BROKEN to demonstrate checkpointing.

    When skip_db=False (default): raises an Exception — simulating a crash.
    When skip_db=True (set via checkpoint retry): succeeds — simulating a fix.

    The key insight: LangGraph checkpoints state BEFORE each node runs.
    So when this node crashes, you can fix the code, set skip_db=True
    in the checkpoint state, and resume from exactly this point.
    """
    print("\n[Node] SAVE TO DB")

    if state.get("skip_db"):
        print("  ✅ Fixed! Database save completed.")
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "✅ DB save completed (resumed from checkpoint after fix)",
                }
            ]
        }

    # 💥 INTENTIONAL CRASH — this simulates a real bug
    print("  💥 CRASH! Simulating database failure...")
    raise Exception(
        "💥 Database connection refused on port 5432!\n"
        "This crash is INTENTIONAL — it demonstrates LangGraph checkpointing.\n"
        "The state is saved. Click 'Fix & Resume from Checkpoint' to recover."
    )


# ---------------------------------------------------------------------------
# Routers (conditional edge functions)
# ---------------------------------------------------------------------------

def search_router(state: ResearchState) -> str:
    return "search" if state["needs_search"] else "skip_search"


def approval_router(state: ResearchState) -> str:
    return "approved" if state.get("human_approved") else "rejected"
