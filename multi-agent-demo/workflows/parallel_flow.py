from concurrent.futures import ThreadPoolExecutor
from agents.tech_agent import TechAgent
from agents.finance_agent import FinanceAgent
from utils.ollama_client import invoke_ollama


def parallel_execute(company):
    tech = TechAgent()
    finance= FinanceAgent()

    with ThreadPoolExecutor() as executor:
        tech_future = executor.submit(tech.run, company)
        finance_future = executor.submit(finance.run, company)

        tech_result = tech_future.result()
        finance_result = finance_future.result()

    combined_prompt = f"""Based on the following analysis, provide a comprehensive report on {company}:
    Tech Analysis: {tech_result}
    Financial Analysis: {finance_result}
    """
    final_report = invoke_ollama(combined_prompt)
    return final_report