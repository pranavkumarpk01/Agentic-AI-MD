from typing import TypedDict, List, Optional, Annotated
import operator


class ResearchState(TypedDict):
    # Who is asking
    user_id: str

    # The research query
    query: str

    # Conversation messages — auto-appended with operator.add
    messages: Annotated[List[dict], operator.add]

    # Raw results from SerpAPI
    search_results: List[str]

    # LLM-generated summary
    summary: str

    # Facts LLM decided are worth remembering
    memory_facts: List[str]

    # Human approved saving to memory?
    human_approved: bool

    # Did LLM decide a web search is needed?
    needs_search: bool

    # Facts loaded from Redis at the start
    past_memory: List[str]

    # DEMO FLAG: set True to bypass the broken save_to_db node (checkpointing demo)
    skip_db: bool

    # Error message if something failed
    error: Optional[str]
