from agents import (
    researcher,
    writer,
    reviewer
)

from tasks import create_tasks
from crew import create_crew

topic = input("Enter Topic: ")

tasks = create_tasks(
    topic,
    researcher,
    writer,
    reviewer
)

crew = create_crew(
    researcher,
    writer,
    reviewer,
    tasks
)

result = crew.kickoff()

print("\n")
print("="*80)
print("FINAL OUTPUT")
print("="*80)
print(result)