from utils.ollama_client import invoke_ollama

class SupervisorAgent:
    def decide(self, query):
        prompt = f"""
        You are an AI supervisor routing user queries to the correct specialized agent.
        Analyze the following user query: "{query}"
        
        Classify the query into EXACTLY one of these three categories:
        - travel
        - tech
        - finance
        
        CRITICAL: Reply with ONLY the category name. Do not include any intro, explanation, summary, or punctuation.
        """
        print("SupervisorAgent is making a decision...")
        result = invoke_ollama(prompt)
        print(f"SupervisorAgent's decision: {result}")
        return result