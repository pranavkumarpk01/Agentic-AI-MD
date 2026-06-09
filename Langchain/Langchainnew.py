import requests
from langchain.tools import tool
from langchain_ollama import ChatOllama
# We import the modern agent creators instead of initialize_agent
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

# 1. Initialize the local Llama model
llm = ChatOllama(model="llama3.2:3b")

# 2. Define the tools
@tool
def get_bitcoin_price() -> str:
    """
    Get current bitcoin price. Takes no arguments.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        return str(requests.get(url).json())
    except Exception as e:
        return f"Error fetching price: {str(e)}"

@tool
def get_country_info(country: str) -> str:
    """
    Get country information such as population. Pass the country name as a string.
    """
    url = f"https://restcountries.com/v3.1/name/{country}"
    try:
        data = requests.get(url).json()
        return str(data[0])    
    except Exception as e:
        return f"Error fetching country data: {str(e)}"

tools = [get_bitcoin_price, get_country_info]

# 3. Create the explicit ReAct Prompt Template
# The modern agent creator requires this structure to know how to log its thoughts.
prompt = PromptTemplate.from_template(
    "Answer the following questions as best you can. You have access to the following tools:\n\n"
    "{tools}\n\n"
    "Use the following format:\n"
    "Question: the input question you must answer\n"
    "Thought: you should always think about what to do\n"
    "Action: the action to take, should be one of [{tool_names}]\n"
    "Action Input: the input to the action\n"
    "Observation: the result of the action\n"
    "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
    "Thought: I now know the final answer\n"
    "Final Answer: the final answer to the original input question\n\n"
    "Begin!\n\n"
    "Question: {input}\n"
    "Thought:{agent_scratchpad}"
)

# 4. Construct the ReAct agent
agent = create_react_agent(llm, tools, prompt)

# 5. Create the executor loop (replaces initialize_agent)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


# 6. Run the agent
response = agent_executor.invoke(
    {
        "input": """
        Tell me the population of India
        and also current bitcoin price
        """
    }
)

# 7. Print the correct output key
print("\n--- FINAL OUTPUT ---")
print(response["output"])