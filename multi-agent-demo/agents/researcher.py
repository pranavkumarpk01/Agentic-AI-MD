from utils.ollama_client import invoke_ollama

class ResearchAgent:
     def run(self, topic):
        prompt = f"Research the following topic and provide a summary: {topic}"
        return invoke_ollama(prompt)