import hopcolony_core

import pika, threading, atexit, signal
import multiprocessing, sys, logging, json
from enum import Enum

_logger = logging.getLogger(__name__)

def connection(app = None):
    if not app:
        app = hopcolony_core.get_app()
    
    return HopTopicConnection(app)

class OutputType(Enum):
    BYTES = 1
    STRING = 2
    JSON = 3

class MalformedJson(Exception):
    pass

class HopTopicConnection:
    _subscribers = {}
    _publishers = []

    def __init__(self, app, pool_threads = 1):
        self.app = app
        self.pool_threads = pool_threads

        self.host = "topics.hopcolony.io"
        self.port = 32012
        self.credentials = pika.PlainCredentials(self.app.config.identity, self.app.config.token)
        self.parameters = pika.ConnectionParameters(host=self.host, port=self.port, 
                    virtual_host=self.app.config.identity, credentials=self.credentials)

        atexit.register(self.close)

    def start_consuming(self, subscriber):
        _logger.debug(f"Starting to consume from topic \"{subscriber.topic}\"")
        try:
            subscriber.start()
        except KeyboardInterrupt:
            # Will be captured by signal
            pass
        
    def subscribe(self, topic, callback, output_type = OutputType.BYTES):
        subscriber = HopTopicSubscriber(self.parameters, topic, callback, output_type)
        # Start consuming asynchronously so that we can subscribe to more than one
        # topic in the same main thread
        process = multiprocessing.Process(target=self.start_consuming, args = (subscriber,))
        process.start()
        self._subscribers[subscriber] = process
    
    def publisher(self, topic):
        publisher =  HopTopicPublisher(self.parameters, topic)
        self._publishers.append(publisher)
        return publisher
        
    def signal_handler(self, signal, frame):
        _logger.error('You pressed Ctrl+C!')
        sys.exit(0)

    def spin(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        forever = threading.Event()
        forever.wait()
    
    def close(self):
        for sub, process in self._subscribers.items():
            _logger.debug(f"Terminating the consumer of topic \"{sub.topic}\"")
            sub.close()
            process.terminate()
            process.join()
        for publisher in self._publishers:
            publisher.close()
        self._subscribers.clear()
        self._publishers.clear()
        if hasattr(atexit, 'unregister'):
            atexit.unregister(self.close)

class HopTopicSubscriber:
    def __init__(self, parameters, topic, callback, output_type):
        self.topic = topic
        self.callback = callback
        self.output_type = output_type
        self.parameters = parameters
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.topic, exchange_type='fanout')
        result = self.channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.topic, queue=queue_name)
        self.consumer_tag = self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.on_message_callback, 
            auto_ack=True)
    
    def on_message_callback(self, ch, method, props, body):
        if self.output_type == OutputType.BYTES:
            out = body
        elif self.output_type == OutputType.STRING:
            out = body.decode('utf-8')
        elif self.output_type == OutputType.JSON:
            try:
                out = json.loads(body.decode('utf-8'))
            except json.decoder.JSONDecodeError as e:
                raise MalformedJson(f"Malformed json message received on topic \"{self.topic}\": {body}") from e
            
        self.callback(out)

    def start(self):
        self.channel.start_consuming()
    
    def close(self):
        self.channel.basic_cancel(self.consumer_tag)
        self.connection.close()

class HopTopicPublisher:
    def __init__(self, parameters, topic):
        self.topic = topic
        self.parameters = parameters
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()
        self.channel.exchange_declare(exchange=self.topic, exchange_type='fanout')

    def send(self, body, routing_key = ''):
        if isinstance(body, dict):
            body = json.dumps(body)
        return self.channel.basic_publish(exchange=self.topic, routing_key=routing_key, body=body)
    
    def close(self):
        self.connection.close()