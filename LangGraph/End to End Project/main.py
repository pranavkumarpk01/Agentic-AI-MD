"""
Research Intelligence Agent — FastAPI Backend

Key endpoints:
  POST /research              → start a new research session, returns thread_id
  GET  /events/{thread_id}   → SSE stream of real-time execution events
  POST /approve/{thread_id}  → human approves or rejects saving to memory
  POST /retry/{thread_id}    → resume from checkpoint after save_to_db crash
  GET  /memory/{user_id}     → fetch stored facts from Redis
  DELETE /memory/{user_id}   → wipe user's memory
  GET  /checkpoint/{thread_id} → inspect current checkpoint state
"""

import asyncio
import json
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse

from graph import graph

app = FastAPI(title="Research Intelligence Agent")

# ---------------------------------------------------------------------------
# Session store
# Per thread_id: list of events (used as a buffer the SSE endpoint reads from)
# ---------------------------------------------------------------------------

sessions: dict[str, dict] = {}
# sessions[thread_id] = {"events": [...], "status": "running|awaiting_approval|done|error"}


def emit(thread_id: str, event_type: str, **kwargs) -> None:
    """Append an event to the session buffer."""
    if thread_id in sessions:
        sessions[thread_id]["events"].append({"type": event_type, **kwargs})


def serialize_state(update) -> dict:
    """Make a LangGraph state update JSON-safe.
    Guards against tuples/non-dicts that LangGraph emits for interrupt events.
    """
    if not isinstance(update, dict):
        return {"raw": str(update)}
    safe = {}
    for k, v in update.items():
        try:
            json.dumps(v)
            safe[k] = v
        except Exception:
            safe[k] = str(v)
    return safe


# ---------------------------------------------------------------------------
# Serve the UI
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html = Path("static/index.html").read_text()
    return HTMLResponse(html)


# ---------------------------------------------------------------------------
# POST /research — kick off a new research session
# ---------------------------------------------------------------------------

@app.post("/research")
async def start_research(body: dict):
    thread_id = str(uuid.uuid4())
    sessions[thread_id] = {"events": [], "status": "running"}

    initial_state = {
        "user_id": body.get("user_id", "user1"),
        "query": body["query"],
        "messages": [],
        "search_results": [],
        "summary": "",
        "memory_facts": [],
        "human_approved": False,
        "needs_search": True,
        "past_memory": [],
        "skip_db": False,
        "error": None,
    }

    config = {"configurable": {"thread_id": thread_id}}

    def run_graph():
        try:
            for event in graph.stream(initial_state, config, stream_mode="updates"):
                for node_name, state_update in event.items():
                    emit(
                        thread_id,
                        "node_update",
                        node=node_name,
                        data=serialize_state(state_update),
                    )

            # Check if graph paused at an interrupt
            snapshot = graph.get_state(config)
            if snapshot.next:
                paused_at = list(snapshot.next)[0]
                values = snapshot.values
                emit(
                    thread_id,
                    "interrupt",
                    node=paused_at,
                    summary=values.get("summary", ""),
                    memory_facts=values.get("memory_facts", []),
                )
                sessions[thread_id]["status"] = "awaiting_approval"
            else:
                sessions[thread_id]["status"] = "done"
                emit(thread_id, "done")

        except Exception as e:
            sessions[thread_id]["status"] = "error"
            emit(thread_id, "error", message=str(e))

    threading.Thread(target=run_graph, daemon=True).start()
    return {"thread_id": thread_id}


# ---------------------------------------------------------------------------
# GET /events/{thread_id} — SSE stream
# Client passes ?since=N to skip already-seen events (used on reconnect)
# ---------------------------------------------------------------------------

@app.get("/events/{thread_id}")
async def stream_events(thread_id: str, since: int = 0):
    async def generate():
        idx = since
        while True:
            session = sessions.get(thread_id)
            if not session:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
                break

            events = session["events"]
            while idx < len(events):
                evt = events[idx]
                yield f"data: {json.dumps(evt)}\n\n"
                idx += 1
                # Stop streaming if we hit a terminal event
                if evt["type"] in ("done", "fatal"):
                    return

            await asyncio.sleep(0.05)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# POST /approve/{thread_id} — human decision on saving to memory
# ---------------------------------------------------------------------------

@app.post("/approve/{thread_id}")
async def approve(thread_id: str, body: dict):
    approved = body.get("approved", False)
    config = {"configurable": {"thread_id": thread_id}}

    # Inject the human decision into the checkpoint state
    graph.update_state(config, {"human_approved": approved})

    sessions[thread_id]["status"] = "running"

    def resume():
        try:
            for event in graph.stream(None, config, stream_mode="updates"):
                for node_name, state_update in event.items():
                    emit(
                        thread_id,
                        "node_update",
                        node=node_name,
                        data=serialize_state(state_update),
                    )

            sessions[thread_id]["status"] = "done"
            emit(thread_id, "done")

        except Exception as e:
            sessions[thread_id]["status"] = "error"
            emit(thread_id, "error", message=str(e))

    threading.Thread(target=resume, daemon=True).start()
    return {"status": "resumed"}


# ---------------------------------------------------------------------------
# POST /retry/{thread_id} — resume from checkpoint after save_to_db crash
# ---------------------------------------------------------------------------

@app.post("/retry/{thread_id}")
async def retry_from_checkpoint(thread_id: str):
    """
    Demonstrates checkpointing:
    1. save_to_db crashed, but state was checkpointed before it ran
    2. We 'fix' the bug by setting skip_db=True in the checkpoint state
    3. graph.stream(None, config) resumes from save_to_db (now with skip_db=True)
    4. save_to_db succeeds this time
    """
    config = {"configurable": {"thread_id": thread_id}}

    # Apply the 'fix' to the saved checkpoint state
    graph.update_state(config, {"skip_db": True})
    sessions[thread_id]["status"] = "running"

    def resume():
        try:
            for event in graph.stream(None, config, stream_mode="updates"):
                for node_name, state_update in event.items():
                    emit(
                        thread_id,
                        "node_update",
                        node=node_name,
                        data=serialize_state(state_update),
                    )

            sessions[thread_id]["status"] = "done"
            emit(thread_id, "done")

        except Exception as e:
            sessions[thread_id]["status"] = "error"
            emit(thread_id, "error", message=str(e))

    threading.Thread(target=resume, daemon=True).start()
    return {"status": "retrying_from_checkpoint"}


# ---------------------------------------------------------------------------
# GET /memory/{user_id} — read Redis memory
# DELETE /memory/{user_id} — wipe it
# ---------------------------------------------------------------------------

@app.get("/memory/{user_id}")
async def get_memory(user_id: str):
    from memory_store import load_user_memory
    return {"user_id": user_id, "facts": load_user_memory(user_id)}


@app.delete("/memory/{user_id}")
async def clear_memory(user_id: str):
    from memory_store import clear_user_memory
    clear_user_memory(user_id)
    return {"status": "cleared"}


# ---------------------------------------------------------------------------
# GET /checkpoint/{thread_id} — inspect saved checkpoint state
# ---------------------------------------------------------------------------

@app.get("/checkpoint/{thread_id}")
async def get_checkpoint(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snapshot = graph.get_state(config)
        return {
            "next": list(snapshot.next) if snapshot.next else [],
            "metadata": snapshot.metadata,
            "values": {
                k: v
                for k, v in snapshot.values.items()
                if k not in ("messages",)  # skip verbose fields
            },
        }
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
