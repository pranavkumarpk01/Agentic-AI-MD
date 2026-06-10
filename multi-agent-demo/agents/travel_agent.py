from utils.ollama_client import invoke_ollama

class TravelAgent:
    def run(self, query):
        prompt = f"Provide a detailed travel guide for {query}"
        return invoke_ollama(prompt)