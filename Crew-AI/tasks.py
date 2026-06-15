from crewai import Task

def create_tasks(topic):

    main_task = Task(
        description=f"""
        Create a complete professional report on:

        {topic}

        The final output must include:

        1. Topic overview
        2. Current trends
        3. Benefits
        4. Challenges
        5. Real-world examples
        6. Statistics
        7. Conclusion

        Use the available specialists appropriately.
        """,
        expected_output="""
        A complete publication-ready report.
        """
    )

    return [main_task]