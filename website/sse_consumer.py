from flask import json
from Queue import Queue


class SSEConsumer():
    def __init__(self, producer):
        self.producer = producer

    def consume(self):
        queue = Queue(1)
        self.producer.add_queue(queue)
        try:
            while True:
                yield 'data: %s\n\n' % json.dumps(queue.get())
        except GeneratorExit:
            self.producer.remove_queue(queue)
