import pika, logging
from enum import Enum

from .queue import *

_logger = logging.getLogger(__name__)

class ExchangeType(Enum):
    DIRECT = 1
    FANOUT = 2
    TOPIC = 3

class HopTopicExchange:
    def __init__(self, channel, name, create, type=ExchangeType.TOPIC, durable=False, auto_delete=False):
        self.channel = channel
        self.name = name
        self.create = create
        self.type = type
        self.durable = durable
        self.auto_delete = auto_delete

        if self.create:
            self.channel.exchange_declare(exchange=self.name, exchange_type=self.str_type, durable=self.durable, auto_delete=self.auto_delete)
    
    @property
    def str_type(self):
        if self.type == ExchangeType.DIRECT:
            return "direct"
        if self.type == ExchangeType.FANOUT:
            return "fanout"
        return "topic"
    
    def listen(self, callback, output_type = OutputType.STRING):
        queue = HopTopicQueue(self.channel, exchange = self.name)
        return queue.listen(callback, output_type=output_type)
  
    def send(self, body):
        if isinstance(body, dict):
            body = json.dumps(body)
        return self.channel.basic_publish(exchange=self.name, routing_key="", body=body)

    def topic(self, name):
        return HopTopicQueue(self.channel, exchange = self.name, binding = name)

    def queue(self, name):
        return HopTopicQueue(self.channel, exchange = self.name, name = name, binding = name)