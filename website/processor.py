from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from threading import Event, Thread

from flask import json

from consumer import SimpleQueueConsumer
from consumer import EmptyTimeoutQueueConsumer


class ProcessorBase(object):
    """An abstract processor."""
    __metaclass__ = ABCMeta

    def __init__(self, producer, consumer):
        super(ProcessorBase, self).__init__()
        self._producer = producer
        self._consumer = consumer

    @property
    def is_finished(self):
        """Are we finished? Default to False / infinite processing."""
        return False

    def _consume(self):
        """Generator for getting consumed items to process."""
        with self._connected():
            while not self.is_finished:
                item = self._consumer.consume()
                if self.is_poison(item):
                    break
                yield item

    @contextmanager
    def _connected(self):
        """Context for managing consumer queue connection to producer."""
        self._producer.add_queue(self._consumer.queue)
        try:
            yield
        finally:
            self._producer.remove_queue(self._consumer.queue)

    @abstractmethod
    def is_poison(self, item):
        """Is the specified item poison? By default, None is poison."""
        return item is None

    @abstractmethod
    def process(self):
        """Process items from the queue."""


class SSEStreamer(ProcessorBase):
    """A simple server-sent events streamer."""
    def __init__(self, producer):
        super(SSEStreamer, self).__init__(producer, SimpleQueueConsumer(1))

    def is_poison(self, item):
        return super(SSEStreamer, self).is_poison(item)

    def process(self):
        for item in self._consume():
            yield 'data: %s\n\n' % json.dumps(item)
        yield 'event: close\nid: CLOSE\ndata: \n\n'


class SocketBroadcaster(ProcessorBase, Thread):
    """A simple socket broadcaster."""
    def __init__(self, socket_io, producer, event, *args, **kwargs):
        super(SocketBroadcaster, self).__init__(
            producer, EmptyTimeoutQueueConsumer(1))
        self.socket_io = socket_io
        self.event = event
        self.args = args
        self.kwargs = kwargs
        self.stop_request = Event()

    @property
    def is_finished(self):
        # We are finished if the thread was stopped.
        return self.stop_request.isSet()

    def is_poison(self, item):
        # It is only poison if it wasn't the result of a timeout.
        if self._consumer.had_timeout:
            return False
        return super(SocketBroadcaster, self).is_poison(item)

    def process(self):
        for item in self._consume():
            if self._consumer.had_timeout:
                # If there was a timeout, skip over the emit.
                continue
            self.socket_io.emit(self.event, item, *self.args, **self.kwargs)

    def run(self):
        self.process()

    def join(self, timeout=None):
        self.stop_request.set()
        super(SocketBroadcaster, self).join(timeout)
