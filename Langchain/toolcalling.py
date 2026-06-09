import requests

from langchain.tools import tool
from langchain_ollama import ChatOllama

#llm = ChatOllama(model="llama3.2:3b")

@tool
def get_bitcoin_price():
    """Get the current price of Bitcoin"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    data = requests.get(url).json()
    return str(data)

@tool
def get_country_info(country : str):
    """ Get Country Information """
    url = f"https://restcountries.com/v3.1/name/{country}"
    data = requests.get(url).json()
    return str(data[0])
    

llm_with_tools = ChatOllama(model="llama3.2:3b", tools=[get_bitcoin_price, get_country_info])    
#llm_with_tools = llm.bind_tools([get_bitcoin_price, get_country_info])

response = llm_with_tools.invoke(" what is Kubernetes?")

print(response.content)