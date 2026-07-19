from utils.jenkins_client import JenkinsClient
from utils.llm_client import OllamaClient

jenkins_client = JenkinsClient()
ollama_client = OllamaClient()


def analyze_failed_build(job_name: str) -> dict:
    """
    Analyze the last failed build using Ollama.
    """
    try:
        logs = jenkins_client.get_console_logs(job_name)
        analysis = ollama_client.analyze_logs(logs)
        return {
            "job": job_name,
            "analysis": analysis
        }
    except Exception as e:
        return {
            "job": job_name,
            "error": str(e)
        }


def summarize_build_status(job_name: str) -> dict:
    """
    Summarize build status using Ollama.
    """
    try:
        build_info = jenkins_client.get_last_build(job_name)
        summary = ollama_client.summarize_build(build_info)
        return {
            "job": job_name,
            "summary": summary
        }
    except Exception as e:
        return {
            "job": job_name,
            "error": str(e)
        }
