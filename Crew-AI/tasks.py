from crewai import Task

def create_tasks(topic, researcher, writer, reviewer):

    research_task = Task(
        description=f"""
        Research the topic:
        {topic}

        Gather:
        - Key concepts
        - Latest trends
        - Benefits
        - Challenges
        """,
        expected_output="Detailed research notes",
        agent=researcher
    )

    writing_task = Task(
        description=f"""
        Using research findings,
        write a professional blog
        on {topic}.
        """,
        expected_output="Complete blog article",
        agent=writer
    )

    review_task = Task(
        description=f"""
        Review the blog on {topic}.

        Improve:
        - Grammar
        - Readability
        - Structure

        Produce final version.
        """,
        expected_output="Final reviewed blog",
        agent=reviewer
    )

    return [
        research_task,
        writing_task,
        review_task
    ]