import hopcolony
from .docs_index import *
from .docs_document import *

import requests
import re


def client(project=None):
    if not project:
        project = hopcolony.get_project()
    if not project:
        raise hopcolony.ConfigNotFound(
            "Hop Config not found. Run 'hopctl login' or place a .hop.config file here.")
    if not project.config.project:
        raise hopcolony.ConfigNotFound(
            "You have no projects yet. Create one at https://console.hopcolony.io")

    return HopDoc(project)


class HopDoc:
    def __init__(self, project):
        self.project = project
        self.client = HopDocClient(project)

    def close(self):
        self.client.close()

    @property
    def status(self):
        try:
            response = self.client.get("/_cluster/health")
            return response.json()
        except requests.exceptions.HTTPError:
            return {"status": "Cluster not reachable"}

    def index(self, index):
        return IndexReference(self.client, index)

    def get(self, filter_hidden=True):
        response = self.client.get("/_cluster/health?level=indices")
        indices = []
        for name, status in response.json()["indices"].items():
            if (not filter_hidden or not re.match(r"\..*", name)) and not re.match(r"ilm-history-.*", name):
                num_docs = self.index(name).count
                indices.append(Index.fromJson(name, status, num_docs))
        return indices


class HopDocClient:
    def __init__(self, project):
        self.project = project
        self.host = "docs.hopcolony.io"
        self.port = 443
        self.identity = project.config.identity
        self._session = requests.Session()
        self._base_url = f"https://{self.host}:{self.port}/{self.identity}/api"

    def close(self):
        self._session.close()

    def get(self, path, **kwargs):
        resp = self._session.request("GET", self._base_url + path, **kwargs)
        resp.raise_for_status()
        return resp

    def post(self, path, **kwargs):
        resp = self._session.request("POST", self._base_url + path, **kwargs)
        resp.raise_for_status()
        return resp

    def put(self, path, **kwargs):
        resp = self._session.request("PUT", self._base_url + path, **kwargs)
        resp.raise_for_status()
        return resp

    def delete(self, path, **kwargs):
        resp = self._session.request("DELETE", self._base_url + path, **kwargs)
        resp.raise_for_status()
        return resp

    # Future<WebSocket> connect(String path) async =>
    #     WebSocket.connect("wss://$host/ws$path")
