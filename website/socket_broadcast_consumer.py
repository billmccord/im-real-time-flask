from threading import Thread
from Queue import Queue


class SocketBroadcastConsumer(Thread):
    def __init__(self, socket_io, producer):
        super(self.__class__, self).__init__()
        self.socket_io = socket_io
        self.producer = producer

    def run(self):
        queue = Queue(1)
        self.producer.add_queue(queue)
        try:
            while True:
                self.socket_io.emit('new-news', queue.get(), namespace='/news')
        except GeneratorExit:
            self.producer.remove_queue(queue)