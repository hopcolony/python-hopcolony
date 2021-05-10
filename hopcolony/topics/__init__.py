import hopcolony
from .queue import *
from .exchange import *
import pika
import asyncio
from signal import SIGINT, SIGTERM
import sys
import logging
import threading
import inspect

_logger = logging.getLogger(__name__)


def connection(project=None):
    if not project:
        project = hopcolony.get_project()
    if not project:
        raise hopcolony.ConfigNotFound(
            "Hop Config not found. Run 'hopctl login' or place a .hop.config file here.")
    if not project.config.project:
        raise hopcolony.ConfigNotFound(
            "You have no projects yet. Create one at https://console.hopcolony.io")

    return HopTopicConnection(project)


class HopTopicConnection:
    open_connections = []

    def __init__(self, project):
        self.project = project

        self.host = "topics.hopcolony.io"
        self.port = 15012
        self.credentials = pika.PlainCredentials(
            self.project.config.identity, self.project.config.token)
        self.parameters = pika.ConnectionParameters(host=self.host, port=self.port,
                                                    virtual_host=self.project.config.identity, credentials=self.credentials)

        self.loops = {}

    def queue(self, name, **kwargs):
        queue = HopTopicQueue(self.add_open_connection,
                              self.parameters, binding=name, name=name)

        # Check if it was decorated
        lines = inspect.stack(context=2)[1].code_context
        decorated = any(line.strip().startswith('@') for line in lines)
        if decorated:
            def _subscribe(cb):
                queue.subscribe(cb, **kwargs)
            return _subscribe
        else:
            return queue
        return

    def exchange(self, name, **kwargs):
        exchange = HopTopicExchange(self.add_open_connection, self.parameters, name, create=kwargs.pop(
            "create", None), type=ExchangeType.FANOUT)

        # Check if it was decorated
        lines = inspect.stack(context=2)[1].code_context
        decorated = [line for line in lines if line.strip().startswith('@')]
        if decorated:
            def _subscribe(cb):
                exchange.subscribe(cb, **kwargs)
            return _subscribe
        else:
            return exchange

    def topic(self, name, **kwargs):
        queue = HopTopicQueue(self.add_open_connection,
                              self.parameters, exchange="amq.topic", binding=name)

        # Check if it was decorated
        lines = inspect.stack(context=2)[1].code_context
        decorated = any(line.strip().startswith('@') for line in lines)
        if decorated:
            def _subscribe(cb):
                queue.subscribe(cb, **kwargs)
            return _subscribe
        else:
            return queue

    def add_open_connection(self, conn):
        self.open_connections.append(conn)

    def signal_handler(self, sig):
        for thread, loop in self.loops.items():
            loop.stop()
            if thread is threading.main_thread():
                _logger.info("Gracefully shutting down")
                loop.remove_signal_handler(SIGTERM)
                loop.add_signal_handler(SIGINT, lambda: None)

    def spin(self, loop=None):
        if not loop:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError as e:
                raise RuntimeError(f"""[ERROR] {e}.""")

        current_thread = threading.current_thread()
        self.loops[current_thread] = loop

        if current_thread is threading.main_thread():
            # Signal handling only works for main thread
            for sig in (SIGTERM, SIGINT):
                loop.add_signal_handler(sig, self.signal_handler, sig)

        loop.run_forever()

        self.close()
        tasks = asyncio.all_tasks(loop=loop)
        for t in tasks:
            t.cancel()
        group = asyncio.gather(*tasks, return_exceptions=True)
        loop.run_until_complete(group)
        loop.close()

    def close(self):
        for conn in self.open_connections:
            conn.cancel()
        self.open_connections.clear()
