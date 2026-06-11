from crewai import Crew, Process

def create_crew(
        researcher,
        writer,
        reviewer,
        tasks
):

    crew = Crew(
        agents=[
            researcher,
            writer,
            reviewer
        ],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    return crew