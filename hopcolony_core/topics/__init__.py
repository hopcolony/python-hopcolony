import hopcolony_core
from .queue import *
from .exchange import *
import pika, atexit, signal
import sys, logging

_logger = logging.getLogger(__name__)

def connection(project = None):
    if not project:
        project = hopcolony_core.get_project()
    if not project:
        raise hopcolony_core.ConfigNotFound("Hop Config not found. Run 'hopctl config set' or place a .hop.config file here.")
    
    return HopTopicConnection(project)

class HopTopicConnection:
    def __init__(self, project):
        self.project = project

        self.host = "topics.hopcolony.io"
        self.port = 32012
        self.credentials = pika.PlainCredentials(self.project.config.identity, self.project.config.token)
        self.parameters = pika.ConnectionParameters(host=self.host, port=self.port, 
                    virtual_host=self.project.config.identity, credentials=self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()

        atexit.register(self.close)

    def queue(self, name):
        return HopTopicQueue(self.channel, binding = name, name = name)

    def exchange(self, name, create = True, type = ExchangeType.TOPIC):
        return HopTopicExchange(self.channel, name, create, type)

    def topic(self, name):
        return HopTopicQueue(self.channel, exchange = "amq.topic", binding = name)        

    def signal_handler(self, signal, frame):
        _logger.error('You pressed Ctrl+C!')
        sys.exit(0)

    def spin(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        forever = threading.Event()
        forever.wait()

    def close(self):
        self.connection.close()
        if hasattr(atexit, 'unregister'):
            atexit.unregister(self.close)