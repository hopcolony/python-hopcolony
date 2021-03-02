import hopcolony_core
from .jobs import *
from .jobs_pipelines import *
from .utils import *

import requests, yaml

def client(project = None):
    if not project:
        project = hopcolony_core.get_project()
    if not project:
        raise hopcolony_core.ConfigNotFound("Hop Config not found. Run 'hopctl login' or place a .hop.config file here.")
    if not project.config.project:
        raise hopcolony_core.ConfigNotFound("You have no projects yet. Create one at https://console.hopcolony.io")
    
    return HopJobs(project)

class HopJobs:
    def __init__(self, project):
        self.project = project
    
    def run(self, job, pipelines = []):
        self.engine = Engine(job, pipelines)
        self.engine.start()
    
    def deploy(self, name, job, pipelines = "", settings = ""):
        cfg = hopcolony_core.config()
        data = {"name": name, "identity": cfg.identity, "job_code": job, "pipelines_code": pipelines, 
            "settings": yaml.dump(settings), "config": yaml.dump(cfg.json)}

        response = requests.post("https://scrape.hopcolony.io/run/", json = data, headers = {"apiKey": cfg.token},
                    timeout = 1)
        assert response.status_code != 403, "Invalid Credentials"
        assert response.status_code != 422, "Uprocessable entity"