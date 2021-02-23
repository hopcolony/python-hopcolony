import hopcolony_core
import hopcolony_core.docs as docs

from .auth_user import *
from .auth_token import *

import requests, re, uuid
from datetime import datetime

def client(project = None):
    if not project:
        project = hopcolony_core.get_project()
    if not project:
        raise hopcolony_core.ConfigNotFound("Hop Config not found. Run 'hopctl config set' or place a .hop.config file here.")
    
    return HopAuth(project)

class DuplicatedEmail(Exception):
    pass

class HopAuth:
    def __init__(self, project):
        self.project = project
        self._docs = docs.HopDoc(project)
    
    def close(self):
        self._docs.close()

    def get(self):
        snapshot = self._docs.index(".hop.auth").get()
        return [HopUser.fromJson(user.source) for user in snapshot.docs]
    
    def user(self, uuid):
        return UserReference(self._docs, uuid)
    
    def register_with_email_and_password(self, email, password, locale = "es"):
        assert email and password, "Email and password can not be empty"
        RESOURCE_ID_NAMESPACE = uuid.UUID('0a7a15ff-aa13-4ac2-897c-9bdf30ce175b')
        uid = str(uuid.uuid5(RESOURCE_ID_NAMESPACE, email))

        snapshot = self._docs.index(".hop.auth").document(uid).get()
        if snapshot.success:
            raise DuplicatedEmail(f"Email {email} has already been used")

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        doc = {
            "registerTs" : now,
            "lastLoginTs" : now,
            "provider" : "email",
            "uuid" : uid,
            "email" : email,
            "password": password,
            "locale" : locale,
            "isAnonymous": False
        }
        currentUser = None
        snapshot = self._docs.index(".hop.auth").document(uid).setData(doc)
        if snapshot.success:
            currentUser = HopUser.fromJson(snapshot.doc.source)
        return UserSnapshot(currentUser, success = currentUser is not None)

    def delete(self, uid):
        return self._docs.index(".hop.auth").document(uid).delete()