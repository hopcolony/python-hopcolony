import unittest, os, requests

import hopcolony_core
from hopcolony_core import drive

class TestDrive(unittest.TestCase):
    user_name = "console@hopcolony.io"
    project_name = "console"
    token_name = "supersecret"

    bucket = "hop-test"
    obj = "test"

    def setUp(self):
        self.project = hopcolony_core.initialize(username = self.user_name, project = self.project_name, 
                                             token = self.token_name)
        self.db = drive.client()
        self.img = drive.load_image(os.path.join(os.path.dirname(__file__), "resources", self.obj))
    
    def tearDown(self):
        self.db.close()

    def test_a_initialize(self):
        self.assertNotEqual(self.project.config, None)
        self.assertEqual(self.project.name, self.project_name)

        self.assertEqual(self.db.project.name, self.project.name)
        self.assertEqual(self.db.client.host, "drive.hopcolony.io")
        self.assertEqual(self.db.client.identity, self.project.config.identity)
    
    def test_b_load_image(self):
        with self.assertRaises(FileNotFoundError):
            drive.load_image("whatever")

    def test_c_get_non_existing_bucket(self):
        snapshot = self.db.bucket("whatever").get()
        self.assertFalse(snapshot.success)

    def test_d_create_bucket(self):
        success = self.db.bucket(self.bucket).create()
        self.assertTrue(success)

    def test_e_get_existing_bucket(self):
        snapshot = self.db.bucket(self.bucket).get()
        self.assertTrue(snapshot.success)
    
    def test_f_list_buckets(self):
        buckets = self.db.get()
        self.assertIn(self.bucket, [bucket.name for bucket in buckets])

    def test_g_delete_bucket(self):
        result = self.db.bucket(self.bucket).delete()
        self.assertTrue(result)

    def test_h_delete_non_existing_bucket(self):
        result = self.db.bucket(self.bucket).delete()
        self.assertTrue(result)

    def test_i_create_object(self):
        snapshot = self.db.bucket(self.bucket).object(self.obj).put(self.img)
        self.assertTrue(snapshot.success)
    
    def test_j_find_object(self):
        snapshot = self.db.bucket(self.bucket).get()
        self.assertTrue(snapshot.success)
        self.assertIn(self.obj, [obj.id for obj in snapshot.objects])

    def test_k_get_object(self):
        snapshot = self.db.bucket(self.bucket).object(self.obj).get()
        self.assertTrue(snapshot.success)
        self.assertEqual(self.obj, snapshot.object.id)
        self.assertEqual(self.img, snapshot.object.data)
    
    def test_l_get_presigned_object(self):
        url = self.db.bucket(self.bucket).object(self.obj).get_presigned()
        response = requests.get(url)
        self.assertEqual(self.img, response.content)
    
    def test_m_delete_object(self):
        result = self.db.bucket(self.bucket).object(self.obj).delete()
        self.assertTrue(result)

    def test_n_add_object(self):
        snapshot = self.db.bucket(self.bucket).add(self.img)
        self.assertTrue(snapshot.success)
        self.assertNotEqual(snapshot.object.id, None)

    def test_o_delete_bucket(self):
        result = self.db.bucket(self.bucket).delete()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()