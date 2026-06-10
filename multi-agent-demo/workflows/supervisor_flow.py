from agents.supervisor import SupervisorAgent
from agents.tech_agent import TechAgent
from agents.finance_agent import FinanceAgent
from agents.travel_agent import TravelAgent

def supervisor_execute(query):
    supervisor = SupervisorAgent()
    decision = supervisor.decide(query)
    
    # 1. Print the raw decision from the LLM
    print(f"\n[DEBUG] Raw Supervisor Decision: '{decision}'")
    
    # Normalize to lowercase for matching
    decision_lower = decision.lower()
    print(f"[DEBUG] Normalized Decision (Lowercase): '{decision_lower}'")

    # 2. Track which condition triggers
    if "travel" in decision_lower or "trip" in decision_lower: # Added 'trip' as a safeguard
        print("[DEBUG] Routing triggered: 'travel' logic matched.")
        travel_agent = TravelAgent()
        return travel_agent.run(query)
        
    elif "tech" in decision_lower:
        print("[DEBUG] Routing triggered: 'tech' logic matched.")
        tech_agent = TechAgent()
        return tech_agent.run(query)
        
    elif "finance" in decision_lower:
        print("[DEBUG] Routing triggered: 'finance' logic matched.")
        finance_agent = FinanceAgent()
        return finance_agent.run(query)
        
    else:
        print("[DEBUG] Routing failed: No keywords matched the supervisor's decision.")
        return f"Supervisor could not decide. Raw decision was: {decision}"