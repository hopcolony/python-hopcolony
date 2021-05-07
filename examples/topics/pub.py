import hopcolony_core
from hopcolony_core import topics

hopcolony_core.initialize()

conn = topics.connection()

conn.topic("topic-cat").send({"data": "Hello"})
conn.exchange("broadcast").send("Hello")
conn.queue("queue-test").send("Hello")
