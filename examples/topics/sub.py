import hopcolony_core
from hopcolony_core import topics
import time
import threading, asyncio

hopcolony_core.initialize()

conn = topics.connection()
threading.Thread(target=lambda: topics.connection())

print(f"Main thread identity: {threading.get_ident()}")

async def queue_cb(msg):
    await asyncio.sleep(1)
    print(f"[QUEUE, {threading.get_ident()}] {msg}")

conn.queue("queue-test").subscribe(queue_cb)
conn.topic("topic-cat").subscribe(lambda msg: print(f"[CAT, {threading.get_ident()}] {msg}"))
conn.exchange("broadcast", create=True).subscribe(lambda msg: print(f"[BROADCAST, {threading.get_ident()}] {msg}"))

conn.spin()


# def run():
#     hopcolony_core.initialize()

#     conn = topics.connection()

#     print(f"Main thread identity: {threading.get_ident()}")

#     async def queue_cb(msg):
#         await asyncio.sleep(1)
#         print(f"[QUEUE, {threading.get_ident()}] {msg}")

#     conn.queue("queue-test").subscribe(queue_cb)
#     conn.topic("topic-cat").subscribe(lambda msg: print(f"[CAT, {threading.get_ident()}] {msg}"))
#     conn.exchange("broadcast", create=True).subscribe(lambda msg: print(f"[BROADCAST, {threading.get_ident()}] {msg}"))

#     conn.spin()

# t = threading.Thread(target=run)
# t.start()