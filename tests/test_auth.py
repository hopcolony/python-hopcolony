import pytest
import time
from .config import *
import hopcolony
from hopcolony import auth


@pytest.fixture
def project():
    return hopcolony.initialize(username=user_name, project=project_name,
                                     token=token)


@pytest.fixture
def db():
    return auth.client()


class TestAuth(object):

    email = "lpaarup@hopcolony.io"
    password = "secret"
    uid = "faad1898-1796-55ca-aa3d-5eec87f8655e"

    def test_a_initialize(self, project, db):
        assert project.config != None
        assert project.name == project_name
        assert db.project.name == project.name

    def test_b_register_with_username_and_password(self, db):
        result = db.register_with_email_and_password(
            self.email, self.password)
        result.success == True
        user = result.user
        assert user.provider == "email"
        assert user.email == self.email
        assert user.password == self.password
        assert user.uuid != None

    def test_c_register_duplicated(self, db):
        with pytest.raises(auth.DuplicatedEmail):
            result = db.register_with_email_and_password(
                self.email, self.password)

    def test_d_list_users(self, db):
        # It takes some time to index the previous addition
        time.sleep(1)
        users = db.get()
        assert self.email in [user.email for user in users]

    def test_e_delete_user(self, db):
        result = db.delete(self.uid)
