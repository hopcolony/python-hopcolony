import unittest

import hopcolony_core
from hopcolony_core import topics
import time, json

class TestTopics(unittest.TestCase):
    user_name = "core@hopcolony.io"
    project_name = "core"
    token_name = "supersecret"

    topic = "test-topic"
    data_string = "Test Message"
    data_json = {"data": "Testing Hop Topics!"}

    def setUp(self):
        self.project = hopcolony_core.initialize(username = self.user_name, project = self.project_name, 
                                             token = self.token_name)
        self.conn = topics.connection()
    
    def test_a_initialize(self):
        self.assertNotEqual(self.project.config, None)
        self.assertEqual(self.project.name, self.project_name)

        self.assertEqual(self.conn.project.name, self.project.name)
        self.assertEqual(self.conn.host, "topics.hopcolony.io")
        self.assertEqual(self.conn.credentials.username, self.project.config.identity)
        self.assertEqual(self.conn.credentials.password, self.project.config.token)

    def test_b_subscriber_publisher_string(self):
        subscription = self.conn.topic(self.topic).listen(lambda msg: self.assertEqual(msg, self.data_string), 
                    output_type=topics.OutputType.STRING)
        time.sleep(0.1)
        self.conn.topic(self.topic).send(self.data_string)
        time.sleep(0.3)
        self.conn.close()
        subscription.close()
        time.sleep(0.2)

    def test_c_subscriber_publisher_good_json(self):
        subscription = self.conn.topic(self.topic).listen(lambda msg: self.assertEqual(msg, self.data_json), 
                    output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        self.conn.topic(self.topic).send(self.data_json)
        time.sleep(0.3)
        self.conn.close()
        subscription.close()
        time.sleep(0.2)

if __name__ == '__main__':
    unittest.main()