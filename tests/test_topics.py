import unittest
from config import *
import hopcolony_core
from hopcolony_core import topics
import time
import json
import sys


class TestTopics(unittest.TestCase):

    topic = "test-topic"
    exchange = "test"
    data_string = "Test Message"
    data_json = {"data": "Testing Hop Topics!"}

    def setUp(self):
        self.project = hopcolony_core.initialize(username=user_name, project=project_name,
                                                 token=token)
        self.conn = topics.connection()

    def tearDown(self):
        self.conn.close()

    def test_a_initialize(self):
        self.assertNotEqual(self.project.config, None)
        self.assertEqual(self.project.name, project_name)

        self.assertEqual(self.conn.project.name, self.project.name)
        self.assertEqual(self.conn.host, "topics.hopcolony.io")
        self.assertEqual(self.conn.credentials.username,
                         self.project.config.identity)
        self.assertEqual(self.conn.credentials.password,
                         self.project.config.token)

    def test_b_subscriber_publisher_string(self):
        self.conn.topic(self.topic).subscribe(lambda msg: self.assertEqual(msg, self.data_string),
                                              output_type=topics.OutputType.STRING)
        time.sleep(0.1)
        self.conn.topic(self.topic).send(self.data_string)
        time.sleep(0.1)
        self.conn.close()

    def test_c_subscriber_publisher_good_json(self):
        self.conn.topic(self.topic).subscribe(lambda msg: self.assertEqual(msg, self.data_json),
                                              output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        self.conn.topic(self.topic).send(self.data_json)
        time.sleep(0.1)
        self.conn.close()

    def test_d_exchange_topic(self):
        self.conn.exchange(self.exchange).topic(self.topic).subscribe(lambda msg: self.assertEqual(msg, self.data_json),
                                                                      output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        self.conn.exchange(self.exchange).topic(
            self.topic).send(self.data_json)
        time.sleep(0.1)
        self.conn.close()

    def test_e_exchange_queue(self):
        self.conn.exchange(self.exchange).queue(self.topic).subscribe(lambda msg: self.assertEqual(msg, self.data_json),
                                                                      output_type=topics.OutputType.JSON)
        self.conn.exchange(self.exchange).queue(self.topic).subscribe(lambda msg: self.assertEqual(msg, self.data_json),
                                                                      output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        self.conn.exchange(self.exchange).queue(
            self.topic).send(self.data_json)
        self.conn.exchange(self.exchange).queue(
            self.topic).send(self.data_json)
        time.sleep(0.1)
        self.conn.close()


if __name__ == '__main__':
    unittest.main()
