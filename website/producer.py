from abc import ABCMeta, abstractmethod
from threading import Lock, Thread, Event
from werkzeug._internal import _log
from time import sleep, strftime


class ProducerBase(object):
    """An abstract base class for producers that is thread-safe."""
    __metaclass__ = ABCMeta

    def __init__(self):
        super(ProducerBase, self).__init__()
        # mutex must be held whenever the queues are mutating. All methods
        # that acquire mutex must release it before returning.
        self.mutex = Lock()
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


class NewsProducer(ProducerBase, Thread):
    def __init__(self):
        super(NewsProducer, self).__init__()
        self.news_count = 0
        self.stop_request = Event()

    def _put(self, item, queue):
        queue.put(item)

    def run(self):
        while not self.stop_request.isSet():
            if self.queue_count > 0:
                self.news_count += 1
                if self.news_count > 10:
                    _log('info', 'Sending poison pill!')
                    self.poison()
                    self.news_count = 0
                else:
                    _log('info', 'Producing news: %d' % self.news_count)
                    item = self.generate_news(self.news_count)
                    self.produce(item)
            sleep(2)

    def join(self, timeout=None):
        self.stop_request.set()
        super(NewsProducer, self).join(timeout)

    @staticmethod
    def generate_news(news_count):
        return \
            {
                "content": "The content for the news story %d." % (++news_count),
                "date": strftime('%Y/%m/%d'),
                "headline": "News story %d" % news_count,
                "icon": "",
                "source": "Source %d" % news_count
            }
