import unittest

import hopcolony_core
from hopcolony_core import topics
import time, json

class TestTopics(unittest.TestCase):
    user_name = "console@hopcolony.io"
    project_name = "console"
    token_name = "supersecret"

    topic = "test-topic"
    data_string = "Test Message"
    data_json = {"data": "Testing Hop Topics!"}

    def setUp(self):
        self.project = hopcolony_core.initialize(username = self.user_name, project = self.project_name, 
                                             token = self.token_name)
    
    def test_a_initialize(self):
        self.assertNotEqual(self.project.config, None)
        self.assertEqual(self.project.name, self.project_name)

        self.conn = topics.connection()
        self.assertEqual(self.conn.project.name, self.project.name)
        self.assertEqual(self.conn.host, "topics.hopcolony.io")
        self.assertEqual(self.conn.credentials.username, self.project.config.identity)
        self.assertEqual(self.conn.credentials.password, self.project.config.token)

    def test_c_subscriber_publisher_string(self):
        self.conn = topics.connection()
        publisher = self.conn.publisher(self.topic)
        subscriber = self.conn.subscribe(self.topic, lambda msg: self.assertEqual(msg, self.data_string), 
                    output_type=topics.OutputType.STRING)
        time.sleep(0.1)
        publisher.send(self.data_string)
        time.sleep(0.3)
        self.conn.close()
        time.sleep(0.2)

    def test_d_subscriber_publisher_good_json(self):
        self.conn = topics.connection()
        publisher = self.conn.publisher(self.topic)
        subscriber = self.conn.subscribe(self.topic, lambda msg: self.assertEqual(msg, self.data_json), 
                    output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        publisher.send(self.data_json)
        time.sleep(0.3)
        self.conn.close()
        time.sleep(0.2)

if __name__ == '__main__':
    unittest.main()