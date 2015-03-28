from abc import ABCMeta, abstractmethod
from gevent.lock import RLock


class ProducerBase(object):
    """An abstract, thread-safe producer."""
    __metaclass__ = ABCMeta

    def __init__(self):
        super(ProducerBase, self).__init__()
        # mutex must be held whenever the queues are mutating. All methods
        # that acquire mutex must release it before returning.
        self.mutex = RLock()
        self.queues = list()

    def add_queue(self, queue):
        """Add a queue to the producer to receive items."""
        with self.mutex:
            self.queues.append(queue)

    def remove_queue(self, queue):
        """Remove a queue from the producer."""
        with self.mutex:
            self.queues.remove(queue)

    @property
    def queue_count(self):
        """Get a count of the queues."""
        with self.mutex:
            return len(self.queues)

    def produce(self, item):
        """Put a produced item on the queue."""
        with self.mutex:
            for queue in self.queues:
                self._put(item, queue)

    def poison(self):
        """Put a 'poison item' on the queues to indicate we are done."""
        with self.mutex:
            for queue in self.queues:
                self._put(self.get_poison, queue)

    @property
    def get_poison(self):
        """Get the poison item. By default, this is None."""
        return None

    @abstractmethod
    def _put(self, item, queue):
        """Put an item in the queue. This is abstract because put will behave
        differently depending on the type of queue used. Also, you may want
        to put items on a queue from another thread so that you can avoid
        blocking."""


class SimpleQueueProducer(ProducerBase):
    """A producer for a basic Queue implementation."""
    def __init__(self, block=True, timeout=None):
        super(SimpleQueueProducer, self).__init__()
        self.block = block
        self.timeout = timeout

    def _put(self, item, queue):
        queue.put(item, self.block, self.timeout)