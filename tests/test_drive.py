import pytest
import os
import requests
from .config import *
import hopcolony
from hopcolony import drive

obj = "test"


@pytest.fixture
def project():
    return hopcolony.initialize(username=user_name, project=project_name,
                                     token=token)


@pytest.fixture
def db():
    return drive.client()


@pytest.fixture
def img():
    return drive.load_image(os.path.join(
        os.path.dirname(__file__), "resources", obj))


class TestDrive(object):

    bucket = "hop-test"
    obj = "test"

    def test_a_initialize(self, project, db):
        assert project.config != None
        assert project.name == project_name

        assert db.project.name == project.name
        assert db.client.host == "drive.hopcolony.io"
        assert db.client.identity == project.config.identity

    def test_b_load_image(self):
        with pytest.raises(FileNotFoundError):
            drive.load_image("whatever")

    def test_c_get_non_existing_bucket(self, db):
        snapshot = db.bucket("whatever").get()
        assert snapshot.success == False

    def test_d_create_bucket(self, db):
        success = db.bucket(self.bucket).create()
        assert success == True

    def test_e_get_existing_bucket(self, db):
        snapshot = db.bucket(self.bucket).get()
        assert snapshot.success == True

    def test_f_list_buckets(self, db):
        buckets = db.get()
        assert self.bucket in [bucket.name for bucket in buckets]

    def test_g_delete_bucket(self, db):
        result = db.bucket(self.bucket).delete()
        assert result == True

    def test_h_delete_non_existing_bucket(self, db):
        result = db.bucket(self.bucket).delete()
        assert result == True

    def test_i_create_object(self, db, img):
        snapshot = db.bucket(self.bucket).object(obj).put(img)
        assert snapshot.success == True

    def test_j_find_object(self, db):
        snapshot = db.bucket(self.bucket).get()
        assert snapshot.success == True
        assert obj in [obj.id for obj in snapshot.objects]

    def test_k_get_object(self, db, img):
        snapshot = db.bucket(self.bucket).object(obj).get()
        assert snapshot.success == True
        assert obj == snapshot.object.id
        assert img == snapshot.object.data

    def test_l_get_presigned_object(self, db, img):
        url = db.bucket(self.bucket).object(obj).get_presigned()
        response = requests.get(url)
        assert response.content == img

    def test_m_delete_object(self, db):
        result = db.bucket(self.bucket).object(obj).delete()
        assert result == True

    def test_n_add_object(self, db, img):
        snapshot = db.bucket(self.bucket).add(img)
        assert snapshot.success == True
        assert snapshot.object.id != None

    def test_o_delete_bucket(self, db):
        result = db.bucket(self.bucket).delete()
        assert result == True
