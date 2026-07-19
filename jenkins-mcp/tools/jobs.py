from utils.jenkins_client import JenkinsClient

client = JenkinsClient()

def list_jobs():
    """
    List all the Jenkins Jobs.
    """
    return client.get_jobs()

def get_job(job_name: str):
    """
    Get details of a specific job
    """
    return client.get_job(job_name)
