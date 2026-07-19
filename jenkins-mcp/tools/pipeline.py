from utils.jenkins_client import JenkinsClient

client = JenkinsClient()


def failed_jobs():
    """
    Return all failed Jenkins jobs.
    """
    jobs = client.get_jobs()

    failed_jobs_list = []

    for job in jobs:
        try:
            build = client.get_last_build(job["name"])
            if build and build.get("result") == "FAILURE":
                failed_jobs_list.append({
                    "job": job["name"],
                    "build": build["number"]
                })
        except:
            pass

    return failed_jobs_list
