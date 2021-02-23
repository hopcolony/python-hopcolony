import unittest, time

import hopcolony_core
from hopcolony_core import auth

class TestAuth(unittest.TestCase):
    app_name = "core"
    project_name = "hop-core"
    token_name = "supersecret"

    email = "lpaarup@hopcolony.io"
    password = "secret"
    uid = "faad1898-1796-55ca-aa3d-5eec87f8655e"

    def setUp(self):
        self.app = hopcolony_core.initialize(app = self.app_name, project = self.project_name, 
                                             token = self.token_name)
        self.db = auth.client()
    
    def tearDown(self):
        self.db.close()

    def test_a_initialize(self):
        self.assertNotEqual(self.app.config, None)
        self.assertEqual(self.app.name, self.app_name)
        self.assertEqual(self.db.app.name, self.app.name)

    def test_b_register_with_username_and_password(self):
        result = self.db.register_with_email_and_password(self.email, self.password)
        self.assertTrue(result.success)
        user = result.user
        self.assertEqual(user.provider, "email")
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.password, self.password)
        self.assertNotEqual(user.uuid, None)
    
    def test_c_register_duplicated(self):
        with self.assertRaises(auth.DuplicatedEmail):
            result = self.db.register_with_email_and_password(self.email, self.password)

    def test_d_list_users(self):
        # It takes some time to index the previous addition
        time.sleep(2)
        users = self.db.get()
        self.assertIn(self.email, [user.email for user in users])

    def test_e_delete_user(self):
        result = self.db.delete(self.uid)

if __name__ == '__main__':
    unittest.main()