from utils.jenkins_client import JenkinsClient

client = JenkinsClient()


def trigger_build(job_name: str):
    """
    Trigger a Jenkins build.
    """
    return client.trigger_build(job_name)


def last_build(job_name: str):
    """
    Get last build information.
    """
    return client.get_last_build(job_name)


def console_logs(job_name: str):
    """
    Fetch console logs of the latest build.
    """
    return client.get_console_logs(job_name)
