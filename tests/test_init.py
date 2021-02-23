import unittest

import hopcolony_core

class TestInitialize(unittest.TestCase):
    user_name = "user"
    project_name = "project"
    token_name = "token"

    def test_initialize(self):
        with self.assertRaises(hopcolony_core.ConfigNotFound):
            hopcolony_core.initialize(config_file = "..")

        with self.assertRaises(hopcolony_core.InvalidConfig):
            hopcolony_core.initialize(username = self.user_name)
        
        with self.assertRaises(hopcolony_core.InvalidConfig):
            hopcolony_core.initialize(username = self.user_name, project = self.project_name)
        
        project = hopcolony_core.initialize(username = self.user_name, project = self.project_name, 
                                       token = self.token_name)
        self.assertEqual(project.config.username, self.user_name)
        self.assertEqual(project.config.project, self.project_name)
        self.assertEqual(project.config.token, self.token_name)

if __name__ == '__main__':
    unittest.main()