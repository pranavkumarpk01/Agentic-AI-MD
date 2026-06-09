from utils.ollama_client import invoke_ollama

class WriterAgent:
    def run(self, research):
        prompt = f"Write a detailed article on the following topic: {research}"
        return invoke_ollama(prompt)