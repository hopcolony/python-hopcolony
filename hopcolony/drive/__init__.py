import hopcolony
from .drive_signer import *
from .drive_bucket import *
from .drive_object import *

from bs4 import BeautifulSoup
from datetime import datetime


def client(project=None):
    if not project:
        project = hopcolony.get_project()
    if not project:
        raise hopcolony.ConfigNotFound(
            "Hop Config not found. Run 'hopctl login' or place a .hop.config file here.")
    if not project.config.project:
        raise hopcolony.ConfigNotFound(
            "You have no projects yet. Create one at https://console.hopcolony.io")

    return HopDrive(project)


def load_image(path):
    with open(path, "rb") as image:
        f = image.read()
        return bytearray(f)


class HopDrive:
    def __init__(self, project):
        self.project = project
        self.client = HopDriveClient(project)

    def close(self):
        self.client.close()

    def bucket(self, bucket):
        return BucketReference(self.client, bucket)

    def get(self):
        response = self.client.get("/")
        soup = BeautifulSoup(response.text, features="html.parser")
        buckets = []
        for soup in soup.find_all("bucket"):
            name = soup.find("name").text
            creation_date = datetime.strptime(
                soup.find("creationdate").text, '%Y-%m-%dT%H:%M:%S.%fZ')
            num_objs = 0
            try:
                # Get the objects in the bucket
                snapshot = self.bucket(name).get()
                if snapshot.success:
                    num_objs = len(snapshot.objects)
            except requests.exceptions.HTTPError:
                pass
            buckets.append(Bucket(name, creation_date, num_objs))
        return buckets


class HopDriveClient:
    def __init__(self, project):
        self.project = project
        self.host = "drive.hopcolony.io"
        self.port = 443
        self.identity = project.config.identity
        self._session = requests.Session()
        self.base_url = f"https://{self.host}:{self.port}/{self.identity}"
        self.signer = drive_signer.Signer(
            self.host, project.config.project, project.config.token)

    def close(self):
        self._session.close()

    def get(self, path):
        signDetails = self.signer.sign("GET", path)
        resp = self._session.request(
            "GET", self.base_url + path, headers=signDetails.headers)
        resp.raise_for_status()
        return resp

    def put(self, path, bodyBytes):
        signDetails = self.signer.sign("PUT", path, bodyBytes=bodyBytes)
        resp = self._session.request(
            "PUT", self.base_url + path, headers=signDetails.headers, data=bodyBytes)
        resp.raise_for_status()
        return resp

    def delete(self, path):
        signDetails = self.signer.sign("DELETE", path)
        resp = self._session.request(
            "DELETE", self.base_url + path, headers=signDetails.headers)
        resp.raise_for_status()
        return resp
