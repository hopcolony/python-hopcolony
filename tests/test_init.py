import unittest

import hopcolony_core

class TestInitialize(unittest.TestCase):
    app_name = "app"
    project_name = "project"
    token_name = "token"

    def test_initialize(self):
        with self.assertRaises(hopcolony_core.ConfigNotFound):
            self.app = hopcolony_core.initialize(config_file = "..")

        with self.assertRaises(hopcolony_core.InvalidConfig):
            hopcolony_core.initialize(app = self.app_name)
        
        with self.assertRaises(hopcolony_core.InvalidConfig):
            hopcolony_core.initialize(app = self.app_name, project = self.project_name)
        
        app = hopcolony_core.initialize(app = self.app_name, project = self.project_name, 
                                       token = self.token_name)
        self.assertEqual(app.config.app, self.app_name)
        self.assertEqual(app.config.project, self.project_name)
        self.assertEqual(app.config.token, self.token_name)

if __name__ == '__main__':
    unittest.main()