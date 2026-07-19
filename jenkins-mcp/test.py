from tools.jobs import list_jobs

jobs = list_jobs()

for job in jobs:
    print(job["name"])