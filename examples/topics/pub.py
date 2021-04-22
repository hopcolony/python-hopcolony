import hopcolony_core
from hopcolony_core import topics

hopcolony_core.initialize()

conn = topics.connection()

conn.topic("topic-example").send("Hello")