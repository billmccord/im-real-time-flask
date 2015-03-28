from time import strftime
import gevent
from gevent.event import Event
from gevent.lock import RLock


class NewsGenerator(object):
    """A simple, example news generator."""
    def __init__(self, producer):
        super(NewsGenerator, self).__init__()
        self.news_count = 0
        self.producer = producer
        self.mutex = RLock()
        self.thread = None
        self.stop_request = Event()

    def generate(self):
        with self.mutex:
            if self.thread is None or self.thread.dead:
                self.stop_request.clear()
                self.news_count = 0
                self.thread = gevent.spawn(self._generate)

    def _generate(self):
        # 10 news articles are always generated regardless of who is listening.
        # We could make this more complex and only generate if someone is
        # listening, but most likely the generator wouldn't even be created
        # unless there was at least one listener.
        while not self.stop_request.is_set() and self.news_count < 10:
            # A small delay for illustrative purposes.
            gevent.sleep(1)
            self.news_count += 1
            # Basically we generate a news article and then send it to the
            # producer.
            item = self.generate_news(self.news_count)
            self.producer.produce(item)
        # When all the news has been produced, we poison the producer and
        # exit the thread.
        self.producer.poison()

    def abort(self, timeout=None):
        with self.mutex:
            if self.thread and not self.thread.dead:
                self.stop_request.set()
                self.thread.join(timeout)

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
