import pika, multiprocessing, json, logging
from enum import Enum

_logger = logging.getLogger(__name__)

class OutputType(Enum):
    BYTES = 1
    STRING = 2
    JSON = 3

class MalformedJson(Exception):
    pass

class HopTopicQueue:
    def __init__(self, connection, exchange = "", binding = "", name = "", durable = False, exclusive = False, auto_delete = True):
        self.connection = connection
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()
        self.exchange = exchange
        self.binding = binding
        self.name = name
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
    
    def subscribe(self, callback, output_type = OutputType.STRING):
        self.callback = callback
        self.output_type = output_type

        result = self.channel.queue_declare(self.name, durable=self.durable, exclusive=self.exclusive, auto_delete=self.auto_delete)
        queue_name = result.method.queue
        if self.exchange:
            self.channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=self.binding)
        self.consumer_tag = self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.on_message_callback, 
            auto_ack=True)

        self.process = multiprocessing.Process(target=self.consume)
        self.process.start()

        return self
    
    def consume(self):
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            pass
    
    def on_message_callback(self, ch, method, props, body):
        if self.output_type == OutputType.BYTES:
            out = body
        elif self.output_type == OutputType.STRING:
            out = body.decode('utf-8')
        elif self.output_type == OutputType.JSON:
            try:
                out = json.loads(body.decode('utf-8'))
            except json.decoder.JSONDecodeError as e:
                raise MalformedJson(f"Malformed json message received on topic \"{self.binding}\": {body}") from e
            
        self.callback(out)

    def send(self, body):
        if isinstance(body, dict):
            body = json.dumps(body)
        return self.channel.basic_publish(exchange=self.exchange, routing_key=self.binding, body=body)

    def close(self):
        self.channel.basic_cancel(self.consumer_tag)
        self.process.terminate()
        self.process.join()