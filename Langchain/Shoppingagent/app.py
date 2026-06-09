from langchain_ollama import ChatOllama

from langchain.agents import (
    create_react_agent,
    AgentExecutor
)

from langchain import hub

from tools import TOOLS

from memory import memory

from db import (
    save_memory,
    get_last_memories
)

# Better than llama3.2 for agents

llm = ChatOllama(
    model="qwen3:8b",
    temperature=0
)

prompt = hub.pull(
    "hwchase17/react"
)

agent = create_react_agent(
    llm=llm,
    tools=TOOLS,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=TOOLS,
    memory=memory,
    verbose=True,
    max_iterations=3,
    early_stopping_method="generate",
    handle_parsing_errors=True
)

print("\nShopping Agent Started")


while True:

    user_query = input(
        "\nAsk: "
    )

    if user_query.lower() == "exit":
        break

    # Long-term memory retrieval

    memories = get_last_memories(
        limit=5
    )

    memory_text = "\n".join(
        [
            f"""
User: {q}
Agent: {a}
"""
            for q, a in memories
        ]
    )

    final_query = f"""
Previous Long Term Memory:

{memory_text}

Current User Question:

{user_query}
"""

    try:

        response = agent_executor.invoke(
            {
                "input": final_query
            }
        )

        answer = response["output"]

        print(
            "\nAgent:",
            answer
        )

        save_memory(
            user_query,
            answer
        )

    except Exception as e:

        print(
            f"\nError: {str(e)}"
        )