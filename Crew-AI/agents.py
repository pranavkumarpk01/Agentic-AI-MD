from crewai import Agent
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:3b", temperature=0.7)

researcher = Agent(
    llm=llm,
    role="Senior Researcher Analyst",
    goal="Conduct in-depth research and analysis on complex topics",
    backstory="You are a seasoned researcher with a keen eye for detail and a passion for uncovering the truth behind various phenomena."
    verbose=True
)

writer = Agent(
    llm=llm,
    role="Creative Writer",
    goal="Craft engaging and compelling narratives based on research findings",
    backstory="You are a talented writer with a flair for storytelling, capable of transforming complex research into captivating articles that resonate with readers.",
    verbose=True
)

reviewer = Agent(
    llm=llm,
    role="Critical Reviewer",
    goal="Provide constructive feedback and critical analysis to improve the quality of written content",
    backstory="You are a meticulous reviewer with a sharp eye for detail, dedicated to enhancing the clarity, coherence, and overall quality of written work through thoughtful critique and suggestions.",
    verbose=True
)