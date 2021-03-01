import pika, multiprocessing, json, logging
from enum import Enum
from dataclasses import dataclass

_logger = logging.getLogger(__name__)

class OutputType(Enum):
    BYTES = 1
    STRING = 2
    JSON = 3

class MalformedJson(Exception):
    pass

@dataclass
class OpenConnection:
    queue: str
    exchange: str
    process: multiprocessing.Process
    connection: pika.adapters.blocking_connection.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel
    consumer_tag: str

    def close(self):
        _logger.debug(f"[{self.consumer_tag}] Closing connection with queue ({self.queue}) and exchange ({self.exchange})")
        self.process.terminate()
        self.process.join()
        self.channel.cancel()
        self.connection.close()
    
    def __str__(self):
        return f"[{self.consumer_tag}] Opened connection with queue ({self.queue}) and exchange ({self.exchange})"

class HopTopicQueue:
    def __init__(self, add_open_connection, parameters, exchange = "", binding = "", name = "", durable = False, exclusive = False, auto_delete = True):
        self.add_open_connection = add_open_connection
        self.parameters = parameters
        self.exchange = exchange
        self.binding = binding
        self.name = name
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
    
    def subscribe(self, callback, output_type = OutputType.STRING):
        self.callback = callback
        self.output_type = output_type

        conn = pika.BlockingConnection(self.parameters)

        channel = conn.channel()
        channel.confirm_delivery()

        result = channel.queue_declare(self.name, durable=self.durable, exclusive=self.exclusive, auto_delete=self.auto_delete)
        queue_name = result.method.queue

        if self.exchange:
            channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=self.binding)
        consumer_tag = channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.on_message_callback, 
            auto_ack=True)

        process = multiprocessing.Process(target=self.consume, args=(channel,))
        process.start()
        
        self.add_open_connection(OpenConnection(self.name, self.exchange, process, conn, channel, consumer_tag))
        return process
    
    def consume(self, channel):
        try:
            channel.start_consuming()
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
        conn = pika.BlockingConnection(self.parameters)

        if isinstance(body, dict):
            body = json.dumps(body)
        
        conn.channel().basic_publish(exchange=self.exchange, routing_key=self.binding, body=body)
        conn.close()