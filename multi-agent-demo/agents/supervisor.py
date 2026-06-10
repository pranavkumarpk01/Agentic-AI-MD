from utils.ollama_client import invoke_ollama

class SupervisorAgent:
    def decide(self, query):
        prompt = f"""As a supervisor, oversee the following topic and provide a comprehensive summary: {query}"""
        return invoke_ollama(prompt)