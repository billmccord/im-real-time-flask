from Queue import Queue, Empty
from abc import ABCMeta, abstractmethod


class ConsumerBase(object):
    """An abstract consumer."""
    __metaclass__ = ABCMeta

    def __init__(self, queue):
        super(ConsumerBase, self).__init__()
        self._queue = queue

    @property
    def queue(self):
        """Get the consumer queue."""
        return self._queue

    @abstractmethod
    def consume(self):
        """Get a single item from the queue."""


class SimpleQueueConsumer(ConsumerBase):
    """A simple consumer backed by a Queue."""
    def __init__(self, maxsize=0, block=True, timeout=None):
        super(SimpleQueueConsumer, self).__init__(Queue(maxsize))
        self._block = block
        self._timeout = timeout

    def consume(self):
        return self.queue.get(self._block, self._timeout)


class EmptyTimeoutQueueConsumer(SimpleQueueConsumer):
    """A SimpleQueueConsumer that handles the Empty timeout."""
    def __init__(self, maxsize=0, timeout=0.5):
        super(EmptyTimeoutQueueConsumer, self).__init__(maxsize, True, timeout)
        self._had_timeout = False

    @property
    def had_timeout(self):
        return self._had_timeout

    def consume(self):
        self._had_timeout = False
        try:
            return super(EmptyTimeoutQueueConsumer, self).consume()
        except Empty:
            self._had_timeout = True
            return None