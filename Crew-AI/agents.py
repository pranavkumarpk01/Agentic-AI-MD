from crewai import Agent, LLM
from dotenv import load_dotenv
from tools import search_tool

load_dotenv()

# =====================================================
# MANAGER (GEMINI)
# =====================================================

manager_llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0
)

# =====================================================
# WORKERS (OLLAMA)
# =====================================================

worker_llm = LLM(
    model="ollama/mistral:7b",
    base_url="http://localhost:11434",
    temperature=0.3
)

# =====================================================
# RESEARCHER
# =====================================================

researcher_agent = Agent(
    role="Senior Research Analyst",

    goal="""
    Always search the internet first.
    Gather current information.
    Verify facts.
    Produce research findings.
    """,

    backstory="""
    You are an expert research analyst.

    RULES:

    - Search before answering.
    - Validate findings.
    - Use internet results.
    - Never depend entirely on memory.
    """,

    tools=[search_tool],

    llm=worker_llm,

    verbose=True,

    allow_delegation=False
)

# =====================================================
# WRITER
# =====================================================

writer_agent = Agent(
    role="Technical Content Writer",
    goal="Convert research into professional content",
    backstory="""
    You are an expert content writer.

    Responsibilities:
    - Write articles
    - Structure content
    - Explain concepts clearly

    Never perform research.
    Only write.
    """,
    llm=worker_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=5
)

# =====================================================
# REVIEWER
# =====================================================

reviewer_agent = Agent(
    role="Senior Editor",
    goal="Review and improve content quality",
    backstory="""
    You are a professional editor.

    Responsibilities:
    - Grammar checking
    - Fact consistency
    - Improve readability
    - Final publication review

    Only review.
    """,
    llm=worker_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=5
)

# =====================================================
# MANAGER
# =====================================================

manager_agent = Agent(
    role="Project Manager",
    goal="Delegate work to the most appropriate specialist and ensure delivery",
    backstory="""
    You are an experienced project manager.

    You do not execute tasks yourself.

    You analyze work and delegate it to:
    - Researcher
    - Writer
    - Reviewer

    Your responsibility is orchestration.
    """,
    llm=manager_llm,
    allow_delegation=True,
    verbose=True,
    max_iter=10
)