import hopcolony_core
from .jobs import *
from .jobs_pipelines import *
from .utils import *

import requests, yaml
import kubernetes.client
from kubernetes.client.rest import ApiException

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ResourceAlreadyExists(Exception):
    pass

def client(project = None):
    if not project:
        project = hopcolony_core.get_project()
    if not project:
        raise hopcolony_core.ConfigNotFound("Hop Config not found. Run 'hopctl login' or place a .hop.config file here.")
    if not project.config.project:
        raise hopcolony_core.ConfigNotFound("You have no projects yet. Create one at https://console.hopcolony.io")
    
    return HopJobs(project)

class HopJobs:
    jobs_cli_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFQaFFUYTVLZ2dzTlMyTzE0ZkJhazdzZ1lhOW9pc3BhSmJUZUl0c0hmUHcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJob3AtY29yZSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJjb3JlLWpvYnMtY2xpLWFjY291bnQtdG9rZW4tcWxtYzIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiY29yZS1qb2JzLWNsaS1hY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNjY0ZTk0ZTktMzg1Yi00NDIzLWEzODYtNjdkYmQzM2E4Mjk1Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmhvcC1jb3JlOmNvcmUtam9icy1jbGktYWNjb3VudCJ9.Gzl-L_S2hZqRkPTeEvW7otq2cA29pq2hPXJvHTRJxQODEmCgupRMnGN9K4mTYD6jzOhgC1e428U-pdYsL5QrYGnilwHhgwB30_mve1WfPosNKYuIcgdBWFHdsB-mS31Mpp-lgZhvRXicOs32VX1gprUbt1vKzgpR27ry6UTUYOiePLON4hpnTh65QRp3ZSNj0TEaWSlPlKLfNVv2eH5QIM4xQ1hwAA9tCx_-AKVQk-LSimlh6xXfTm0YpIj_rvHKqODmEZNIxmpqcBvZXS-PF3jPjc7JKUgKJSc89OkH-vz7tXhSWTRqmGPzfoPvWkUmAdL9V7naZ2XY5x79fvo5Qg"
    def __init__(self, project):
        self.project = project
        self.configuration = kubernetes.client.Configuration()
        self.configuration.host="https://hopcolony.io:8443"
        self.configuration.verify_ssl=False
        self.configuration.debug = False
        self.configuration.api_key["authorization"]=  "Bearer " + self.jobs_cli_token
    
    def run(self, job, pipelines = []):
        self.engine = Engine(job, pipelines)
        self.engine.start()
    
    def deploy(self, name, job, pipelines = "", settings = {}, schedule = None):
        cfg = hopcolony_core.config()
        spec = job_spec.format(kind = "HopCronJob" if schedule else "HopJob", 
                metadata_name = name if schedule else f"job-{name}-{str(time.time()).replace('.', '')}",
                name = name, schedule = f"schedule: '{schedule}'" if schedule else "", 
                job = job.replace("\n", "\n    "), pipelines = pipelines.replace("\n", "\n    "),
                settings = yaml.dump(settings).replace("\n", "\n    "), config = yaml.dump(cfg.json).replace("\n", "\n    "))

        with kubernetes.client.ApiClient(self.configuration) as api_client:
            api_instance = kubernetes.client.CustomObjectsApi(api_client)
        
        try:
            api_instance.create_cluster_custom_object("hopcolony.io", "v1", "hopcronjobs" if schedule else "hopjobs", yaml.load(spec, Loader=yaml.FullLoader))
        except ApiException as e:
            if e.status == 409:
                raise ResourceAlreadyExists