import requests
from config import OLLAMA_URL


class OllamaClient:
    def __init__(self, model: str = "mistral"):
        self.base_url = OLLAMA_URL
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate text using Ollama.
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "No response generated")
        except Exception as e:
            return f"Error: {str(e)}"

    def analyze_logs(self, logs: str) -> str:
        """
        Analyze build logs using Ollama.
        """
        prompt = f"Analyze these build logs and identify issues:\n\n{logs[:2000]}"
        return self.generate(prompt)

    def summarize_build(self, build_info: dict) -> str:
        """
        Summarize build information using Ollama.
        """
        prompt = f"Summarize this Jenkins build:\nJob: {build_info.get('job')}\nStatus: {build_info.get('result')}\nDuration: {build_info.get('duration')}ms"
        return self.generate(prompt)
