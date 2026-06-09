from utils.ollama_client import invoke_ollama

class ReviewerAgent:
    def run(self, article):
        prompt = f"Review the following article and provide feedback: {article}"
        return invoke_ollama(prompt)