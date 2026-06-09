from agents.researcher import ResearchAgent
from agents.writer import WriterAgent
from agents.reviewer import ReviewerAgent

def sequential_flow(topic):
    researcher = ResearchAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()

    # 1. Researcher runs
    research = researcher.run(topic)
    print("Research Summary completed...\n")

    # 2. Writer runs
    article = writer.run(research)
    print("Generated Article completed...\n")
    
    # 3. Reviewer runs
    feedback = reviewer.run(article)
    print("Review Feedback completed...\n")

    
    return {
        "generated_article": article,
        "reviewer_feedback": feedback
    }