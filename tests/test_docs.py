import unittest

import hopcolony_core
from hopcolony_core import docs

class TestDocs(unittest.TestCase):
    user_name = "core@hopcolony.io"
    project_name = "core"
    token_name = "supersecret"

    index = ".hop.tests"
    uid = "hopcolony"
    data = {"purpose": "Test Hop Docs!"}

    def setUp(self):
        self.project = hopcolony_core.initialize(username = self.user_name, project = self.project_name, 
                                             token = self.token_name)
        self.db = docs.client()
    
    def tearDown(self):
        self.db.close()

    def test_a_initialize(self):
        self.assertNotEqual(self.project.config, None)
        self.assertEqual(self.project.name, self.project_name)

        self.assertEqual(self.db.project.name, self.project.name)
        self.assertEqual(self.db.client.host, "docs.hopcolony.io")
        self.assertEqual(self.db.client.identity, self.project.config.identity)

    def test_b_status(self):
        status = self.db.status
        self.assertNotEqual(status["status"], "red")

    def test_c_create_document(self):
        snapshot = self.db.index(self.index).document(self.uid).setData(self.data)
        self.assertTrue(snapshot.success)
        doc = snapshot.doc
        self.assertEqual(doc.index, self.index)
        self.assertEqual(doc.id, self.uid)
        self.assertEqual(doc.source, self.data)

    def test_d_get_document(self):
        snapshot = self.db.index(self.index).document(self.uid).get()
        self.assertTrue(snapshot.success)
        doc = snapshot.doc
        self.assertEqual(doc.index, self.index)
        self.assertEqual(doc.id, self.uid)
        self.assertEqual(doc.source, self.data)

    def test_e_delete_document(self):
        snapshot = self.db.index(self.index).document(self.uid).delete()
        self.assertTrue(snapshot.success)

    def test_f_find_non_existing(self):
        snapshot = self.db.index(self.index).document(self.uid).get()
        self.assertFalse(snapshot.success)

        snapshot = self.db.index(self.index).document(self.uid).update({"data": "test"})
        self.assertFalse(snapshot.success)

        snapshot = self.db.index(self.index).document(self.uid).delete()
        self.assertFalse(snapshot.success)

        snapshot = self.db.index(".does.not.exist").get()
        self.assertFalse(snapshot.success)

    def test_g_create_document_without_id(self):
        snapshot = self.db.index(self.index).add(self.data)
        self.assertTrue(snapshot.success)
        doc = snapshot.doc
        self.assertEqual(doc.index, self.index)
        self.assertEqual(doc.source, self.data)

        snapshot = self.db.index(self.index).document(doc.id).delete()
        self.assertTrue(snapshot.success)

    def test_h_delete_index(self):
        result = self.db.index(self.index).delete()
        self.assertTrue(result)

    def test_i_index_not_there(self):
        result = self.db.get()
        self.assertNotIn(self.index, [index.name for index in result])

if __name__ == '__main__':
    unittest.main()