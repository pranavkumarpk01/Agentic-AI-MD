from utils.ollama_client import invoke_ollama

class TechAgent:
    def run(self, company):
        prompt = f"Provide a detailed analysis of the latest trends in {company}"
        return invoke_ollama(prompt)