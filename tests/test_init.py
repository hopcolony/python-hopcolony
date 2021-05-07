import unittest
from config import *
import hopcolony_core


class TestInitialize(unittest.TestCase):

    def test_initialize(self):
        with self.assertRaises(hopcolony_core.ConfigNotFound):
            hopcolony_core.initialize(config_file="..")

        with self.assertRaises(hopcolony_core.InvalidConfig):
            hopcolony_core.initialize(username=user_name)

        with self.assertRaises(hopcolony_core.InvalidConfig):
            hopcolony_core.initialize(username=user_name, project=project_name)

        project = hopcolony_core.initialize(username=user_name, project=project_name,
                                            token=token)
        self.assertEqual(project.config.username, user_name)
        self.assertEqual(project.config.project, project_name)
        self.assertEqual(project.config.token, token)


if __name__ == '__main__':
    unittest.main()
