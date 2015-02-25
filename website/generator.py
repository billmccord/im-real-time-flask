from threading import Thread, Event
from time import sleep, strftime


class NewsGenerator(Thread):
    """A simple, example news generator."""
    def __init__(self, producer):
        super(NewsGenerator, self).__init__()
        self.news_count = 0
        self.producer = producer
        self.stop_request = Event()

    def run(self):
        # 10 news articles are always generated regardless of who is listening.
        # We could make this more complex and only generate if someone is
        # listening, but most likely the generator wouldn't even be created
        # unless there was at least one listener.
        while not self.stop_request.isSet() and self.news_count < 10:
            # A small delay for illustrative purposes.
            sleep(1)
            self.news_count += 1
            # Basically we generate a news article and then send it to the
            # producer.
            item = self.generate_news(self.news_count)
            self.producer.produce(item)
        # When all the news has been produced, we poison the producer and
        # exit the thread.
        self.producer.poison()

    def join(self, timeout=None):
        self.stop_request.set()
        super(NewsGenerator, self).join(timeout)

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
