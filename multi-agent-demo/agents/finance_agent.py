from utils.ollama_client import invoke_ollama

class FinanceAgent:
    def run(self, company):
        prompt = f"""Financial analysis for {company}:"""
        return invoke_ollama(prompt)