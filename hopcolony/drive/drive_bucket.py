from .drive_object import *
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
from dataclasses import dataclass


@dataclass
class Bucket:
    printable_headers = ["Name", "Number of Objects", "Creation Date"]

    name: str
    creation_date: datetime
    num_objs: int

    @property
    def json(self):
        return {"name": self.name, "creation_date": self.creation_date, "num_objs": self.num_objs}

    @property
    def printable(self):
        return [self.name, self.num_objs, self.creation_date]


class BucketReference:
    def __init__(self, client, bucket):
        self.client = client
        self.bucket = bucket

    def get(self):
        try:
            response = self.client.get(f"/{self.bucket}")
            soup = BeautifulSoup(response.text, features="html.parser")
            objects = []
            for s in soup.find_all("contents"):
                url = self.object(s.find("key").text).get_presigned()
                objects.append(Object.fromSoup(url, s))
            return BucketSnapshot(objects, success=True)
        except requests.exceptions.HTTPError:
            return BucketSnapshot(None, success=False)

    @property
    def exists(self):
        try:
            response = self.client.get(f"/{self.bucket}")
            return True
        except requests.exceptions.HTTPError:
            return False

    def create(self):
        try:
            self.client.put(f"/{self.bucket}", bodyBytes=b"")
            return True
        except requests.exceptions.HTTPError:
            return False

    def add(self, data):
        id = uuid.uuid4().hex.upper()[0:10]
        return self.object(id).put(data)

    def object(self, id):
        if not self.exists:
            success = self.create()
            assert success, f"{self.bucket} did not exist and could not be created"
        return ObjectReference(self.client, self.bucket, id)

    def delete(self):
        # Delete all the objects before deleting the bucket
        if not self.exists:
            # Deleting a non existing bucket
            return True
        else:
            snapshot = self.get()
            for object in snapshot.objects:
                self.object(object.id).delete()
        try:
            self.client.delete(f"/{self.bucket}")
            return True
        except requests.exceptions.HTTPError as e:
            return False


class BucketSnapshot:
    def __init__(self, objects, success=False):
        self.objects = objects
        self.success = success
