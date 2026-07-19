import requests
from requests.auth import HTTPBasicAuth
from config import JENKINS_URL, JENKINS_USER, JENKINS_TOKEN


class JenkinsClient:

    def __init__(self):
        self.auth = HTTPBasicAuth(JENKINS_USER, JENKINS_TOKEN)

    def get_jobs(self):
        url = f"{JENKINS_URL}/api/json"

        response = requests.get(url, auth=self.auth)

        return response.json()["jobs"]


    def trigger_build(self, job_name):
        url = f"{JENKINS_URL}/job/{job_name}/build"

        response = requests.post(url, auth=self.auth)

        return {
            "status": response.status_code
        }


    def get_last_build(self, job_name):
        url = f"{JENKINS_URL}/job/{job_name}/lastBuild/api/json"

        response = requests.get(url, auth=self.auth)

        return response.json()


    def get_console_logs(self, job_name):
        url = f"{JENKINS_URL}/job/{job_name}/lastBuild/consoleText"

        response = requests.get(url, auth=self.auth)

        return response.text