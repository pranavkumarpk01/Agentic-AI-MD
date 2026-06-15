from agents import (
    researcher_agent,
    writer_agent,
    reviewer_agent,
    manager_agent
)

from tasks import create_tasks
from crew import create_crew

def main():

    topic = input("Enter Topic: ")

    tasks = create_tasks(topic)

    crew = create_crew(
        researcher_agent,
        writer_agent,
        reviewer_agent,
        manager_agent,
        tasks
    )

    result = crew.kickoff()

    print("\n")
    print("=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print(result)

if __name__ == "__main__":
    main()