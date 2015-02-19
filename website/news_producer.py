from time import strftime, sleep
from threading import Thread, Lock
from werkzeug._internal import _log


class NewsProducer(Thread):
    queueLock = Lock()
    queues = list()

    def add_queue(self, queue):
        with self.queueLock:
            self.queues.append(queue)

    def remove_queue(self, queue):
        with self.queueLock:
            self.queues.remove(queue)

    def run(self):
        news_count = 0
        while True:
            with self.queueLock:
                if len(self.queues) > 0:
                    news_count += 1
                    _log('info', 'Producing news: %d' % news_count)
                    for queue in self.queues:
                        queue.put(self.generate_news(news_count))
            sleep(5)

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
