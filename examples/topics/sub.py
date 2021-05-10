import hopcolony
from hopcolony import topics
import time
import threading
import asyncio

hopcolony.initialize()

conn = topics.connection()
threading.Thread(target=lambda: topics.connection())

print(f"Main thread identity: {threading.get_ident()}")

# Asyncio coroutine example


async def queue_test(msg):
    await asyncio.sleep(1)
    print(f"[QUEUE, {threading.get_ident()}] {msg}")

conn.queue("queue-test").subscribe(queue_test)

# Decorator example


@conn.topic("topic-cat", output_type=topics.OutputType.JSON)
def topic_cat(msg):
    print(f"[CAT, {threading.get_ident()}] {msg}")


# Lambda example
conn.exchange("broadcast", create=True).subscribe(
    lambda msg: print(f"[BROADCAST, {threading.get_ident()}] {msg}"))

conn.spin()
