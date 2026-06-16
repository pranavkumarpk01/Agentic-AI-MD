from crewai import Crew, Process

def create_crew(
    researcher_agent,
    writer_agent,
    reviewer_agent,
    manager_agent,
    tasks
):

    return Crew(
        agents=[
            researcher_agent,
            writer_agent,
            reviewer_agent
        ],
        tasks=tasks,
        manager_agent=manager_agent,
        process=Process.hierarchical,
        verbose=True,

        memory=True,

        planning=False
    )