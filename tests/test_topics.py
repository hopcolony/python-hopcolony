import pytest
from .config import *
import hopcolony
from hopcolony import topics
import time
import json


@pytest.fixture
def project():
    return hopcolony.initialize(username=user_name, project=project_name,
                                     token=token)


@pytest.fixture
def conn():
    return topics.connection()


class TestTopics(object):

    topic = "test-topic"
    exchange = "test"
    data_string = "Test Message"
    data_json = {"data": "Testing Hop Topics!"}

    def test_a_initialize(self, project, conn):
        assert project.config != None
        assert project.name == project_name

        assert conn.project.name == project.name
        assert conn.host == "topics.hopcolony.io"
        assert conn.credentials.username == project.config.identity
        assert conn.credentials.password == project.config.token

    def test_b_subscriber_publisher_string(self, conn):
        def cb(msg):
            assert msg == self.data_string

        conn.topic(self.topic).subscribe(
            cb, output_type=topics.OutputType.STRING)
        time.sleep(0.1)
        conn.topic(self.topic).send(self.data_string)
        time.sleep(0.1)
        conn.close()

    def test_c_subscriber_publisher_good_json(self, conn):
        def cb(msg):
            assert msg == self.data_json
        conn.topic(self.topic).subscribe(
            cb, output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        conn.topic(self.topic).send(self.data_json)
        time.sleep(0.1)
        conn.close()

    def test_d_exchange_topic(self, conn):
        def cb(msg):
            assert msg == self.data_json
        conn.exchange(self.exchange).topic(self.topic).subscribe(
            cb, output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        conn.exchange(self.exchange).topic(
            self.topic).send(self.data_json)
        time.sleep(0.1)
        conn.close()

    def test_e_exchange_queue(self, conn):
        def cb(msg):
            assert msg == self.data_json
        conn.exchange(self.exchange).queue(self.topic).subscribe(
            cb, output_type=topics.OutputType.JSON)
        conn.exchange(self.exchange).queue(self.topic).subscribe(
            cb, output_type=topics.OutputType.JSON)
        time.sleep(0.1)
        conn.exchange(self.exchange).queue(
            self.topic).send(self.data_json)
        conn.exchange(self.exchange).queue(
            self.topic).send(self.data_json)
        time.sleep(0.1)
        conn.close()
