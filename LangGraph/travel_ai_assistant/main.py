from langchain_core.messages import HumanMessage
from graph.builder import build_graph


def main():
    graph = build_graph()
    print("Travel AI Assistant — type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        result = graph.invoke({"messages": [HumanMessage(content=user_input)]})
        answer = result["messages"][-1].content
        print(f"\nAssistant: {answer}\n")


if __name__ == "__main__":
    main()
