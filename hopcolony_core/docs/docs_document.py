import requests
from dataclasses import dataclass


@dataclass
class Document:

    source: dict
    index: str = None
    id: str = None
    version: int = None

    @classmethod
    def fromJson(cls, json):
        return cls(json["_source"], index=json["_index"], id=json["_id"], version=json["_version"] if "_version" in json else None)

    def __str__(self):
        return f'"source": {self.source}, "index": {self.index}, "id": {self.id}, "version": {self.version}'

    @classmethod
    def printable_headers(self, columns):
        return ['Id', *columns]

    def printable(self, columns):
        data = []
        for column in columns:
            value = self.source[column] if column in self.source else None
            data.append(value)
        return [self.id, *data]


class DocumentSnapshot:
    def __init__(self, doc, success=False, reason=""):
        self.doc = doc
        self.success = success
        self.reason = reason


class DocumentReference:
    def __init__(self, client, index, id):
        self.client = client
        self.index = index
        self.id = id

    def get(self):
        try:
            response = self.client.get(f"/{self.index}/_doc/{self.id}")
            body = response.json()
            return DocumentSnapshot(Document.fromJson(body), success=True)
        except requests.exceptions.HTTPError as e:
            return DocumentSnapshot(None, success=False, reason=str(e))

    def setData(self, doc):
        try:
            response = self.client.post(
                f"/{self.index}/_doc/{self.id}", json=doc)
            body = response.json()
            return DocumentSnapshot(Document(doc, index=self.index, id=body["_id"], version=body["_version"]), success=True)
        except requests.exceptions.HTTPError as e:
            return DocumentSnapshot(None, success=False, reason=str(e))

    def update(self, fields):
        try:
            response = self.client.post(
                f"/{self.index}/_doc/{self.id}/_update", json={"doc": fields})
            return self.get()
        except requests.exceptions.HTTPError as e:
            return DocumentSnapshot(None, success=False, reason=str(e))

    def delete(self):
        try:
            response = self.client.delete(f"/{self.index}/_doc/{self.id}")
            body = response.json()
            return DocumentSnapshot(Document(None, index=self.index, id=body["_id"], version=body["_version"]), success=True)
        except requests.exceptions.HTTPError as e:
            return DocumentSnapshot(None, success=False, reason=str(e))
