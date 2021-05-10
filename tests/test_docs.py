import pytest
from .config import *
import hopcolony
from hopcolony import docs


@pytest.fixture
def project():
    return hopcolony.initialize(username=user_name, project=project_name,
                                     token=token)


@pytest.fixture
def db():
    return docs.client()


class TestDocs(object):

    index = ".hop.tests"
    uid = "hopcolony"
    data = {"purpose": "Test Hop Docs!"}

    def test_a_initialize(self, project, db):
        assert project.config != None
        assert project.name == project_name

        assert db.project.name == project.name
        assert db.client.host == "docs.hopcolony.io"
        assert db.client.identity == project.config.identity

    def test_b_status(self, db):
        status = db.status
        assert status["status"] != "red"

    def test_c_create_document(self, db):
        snapshot = db.index(self.index).document(self.uid).setData(self.data)
        assert snapshot.success == True
        doc = snapshot.doc
        assert doc.index == self.index
        assert doc.id == self.uid
        assert doc.source == self.data

    def test_d_get_document(self, db):
        snapshot = db.index(self.index).document(self.uid).get()
        assert snapshot.success == True
        doc = snapshot.doc
        assert doc.index == self.index
        assert doc.id == self.uid
        assert doc.source == self.data

    def test_e_delete_document(self, db):
        snapshot = db.index(self.index).document(self.uid).delete()
        assert snapshot.success == True

    def test_f_find_non_existing(self, db):
        snapshot = db.index(self.index).document(self.uid).get()
        assert snapshot.success == False

        snapshot = db.index(self.index).document(
            self.uid).update({"data": "test"})
        assert snapshot.success == False

        snapshot = db.index(self.index).document(self.uid).delete()
        assert snapshot.success == False

        snapshot = db.index(".does.not.exist").get()
        assert snapshot.success == False

    def test_g_create_document_without_id(self, db):
        snapshot = db.index(self.index).add(self.data)
        assert snapshot.success == True
        doc = snapshot.doc
        assert doc.index == self.index
        assert doc.source == self.data

        snapshot = db.index(self.index).document(doc.id).delete()
        assert snapshot.success == True

    def test_h_delete_index(self, db):
        result = db.index(self.index).delete()
        assert result == True

    def test_i_index_not_there(self, db):
        result = db.get()
        assert self.index not in [index.name for index in result]
