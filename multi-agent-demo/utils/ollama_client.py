from langchain_community.llms import Ollama

llm = Ollama(model="qwen3:8b")

def invoke_ollama(prompt):
    return llm.invoke(prompt)