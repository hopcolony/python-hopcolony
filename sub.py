import hopcolony_core
from hopcolony_core import topics
import time

hopcolony_core.initialize()

conn = topics.connection()

conn.queue("queue-test").subscribe(lambda msg: print(f"[QUEUE] {msg}"))
conn.topic("topic-cat").subscribe(lambda msg: print(f"[CAT] {msg}"))
conn.exchange("broadcast").subscribe(lambda msg: print(f"[BROADCAST] {msg}"))

time.sleep(3)
conn.queue("queue-test").send("Hello")

time.sleep(3)
conn.topic("topic-cat").send("Hello")

time.sleep(3)
conn.exchange("broadcast").send("Hello")

conn.spin()