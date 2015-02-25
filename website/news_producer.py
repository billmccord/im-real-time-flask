from time import strftime, sleep
from threading import Thread, Lock
from werkzeug._internal import _log


class NewsProducer(Thread):
    queue_lock = Lock()
    queues = list()

    def add_queue(self, queue):
        with self.queue_lock:
            self.queues.append(queue)

    def remove_queue(self, queue):
        with self.queue_lock:
            self.queues.remove(queue)

    def run(self):
        news_count = 0
        while True:
            with self.queue_lock:
                if len(self.queues) > 0:
                    news_count += 1
                    if news_count > 10:
                        _log('info', 'Sending poison pill!')
                        for queue in self.queues:
                            queue.put(None)
                            news_count = 0
                    else:
                        _log('info', 'Producing news: %d' % news_count)
                        for queue in self.queues:
                            queue.put(self.generate_news(news_count))
            sleep(2)

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
