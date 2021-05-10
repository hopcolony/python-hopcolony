import hopcolony
from hopcolony import topics

hopcolony.initialize()

conn = topics.connection()

conn.topic("topic-cat").send({"data": "Hello"})
conn.exchange("broadcast").send("Hello")
conn.queue("queue-test").send("Hello")
