from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from tools import tools
from memory import (
    save_memory,
    retrieve_memory
)
from db import (
    initialize_database,
    save_conversation
)
from prompts import SYSTEM_PROMPT

initialize_database()

llm = ChatOllama(
    model="qwen3:8b",
    temperature=0
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT
)

print("Travel Planner Started")
print("Type exit to quit")

while True:

    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    memory_context = retrieve_memory(
        user_input
    )

    final_prompt = f"""
Previous Memory:

{memory_context}

Current User Query:

{user_input}
"""

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": final_prompt
                }
            ]
        }
    )

    answer = response["messages"][-1].content

    print("\nAI:")
    print(answer)

    save_memory(
        user_input,
        answer
    )

    save_conversation(
        user_input,
        answer
    )