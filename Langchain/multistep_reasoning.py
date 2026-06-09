
import requests
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_classic.agents import initialize_agent, AgentType

llm = ChatOllama(model="llama3.2:3b")

@tool
def get_bitcoin_price():
    """
    Get current bitcoin price
    """

    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    return str(
        requests.get(url).json()
    )

@tool
def get_country_info(country:str):
    """
    Get country information
    """

    url = f"https://restcountries.com/v3.1/name/{country}"

    data = requests.get(url).json()

    return str(data[0])    



tools = [get_bitcoin_price, get_country_info]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

response = agent.invoke(
    {
        "input":
        """
        Tell me the population of India
        and also current bitcoin price
        """
    }
)

print(response.content)