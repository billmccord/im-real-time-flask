from abc import ABCMeta, abstractmethod
from contextlib import contextmanager

from flask import json
import gevent
from gevent.event import Event
from gevent.lock import RLock

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

    @abstractmethod
    def abort(self, timeout=None):
        """Abort processing if possible and block for the specified timeout.
        Typically a processor should end normally or throw an exception if
        it is unable to end by the timeout time (see the join method on a
        Thread.) The default timeout is None which will block forward.
        By default this does method nothing."""
        pass


class SSEStreamer(ProcessorBase):
    """A simple server-sent events streamer."""

    def __init__(self, producer):
        super(SSEStreamer, self).__init__(producer, SimpleQueueConsumer(1))
        # You may optionally specify a method to call when finished or aborted.
        self.finished = None
        self.aborted = None

    def is_poison(self, item):
        return super(SSEStreamer, self).is_poison(item)

    def process(self):
        try:
            for item in self._consume():
                yield 'data: %s\n\n' % json.dumps(item)
            yield 'event: close\nid: CLOSE\ndata: \n\n'
        except GeneratorExit:
            # Typically caused by client disconnect. Unfortunately, an
            # exception is currently thrown when this happens. A known bug:
            # https://github.com/gevent/gevent/issues/445
            #
            # Here is a workaround if we really need it:
            # http://stackoverflow.com/questions/15479902/flask-server-sent-events-socket-exception
            if self.aborted is not None:
                self.aborted()
        finally:
            if self.finished is not None:
                self.finished()

    def abort(self, timeout=None):
        super(SSEStreamer, self).abort(timeout)


class SocketBroadcaster(ProcessorBase):
    """A simple socket broadcaster."""
    def __init__(self, socket_io, producer, event, *args, **kwargs):
        super(SocketBroadcaster, self).__init__(
            producer, EmptyTimeoutQueueConsumer(1))
        self.socket_io = socket_io
        self.event = event
        self.args = args
        self.kwargs = kwargs
        self.mutex = RLock()
        self.thread = None
        self.stop_request = Event()

    @property
    def is_finished(self):
        # We are finished if the thread was stopped.
        return self.stop_request.is_set()

    def is_poison(self, item):
        # It is only poison if it wasn't the result of a timeout.
        if self._consumer.had_timeout:
            return False
        return super(SocketBroadcaster, self).is_poison(item)

    def process(self):
        with self.mutex:
            if self.thread is None or self.thread.dead:
                self.stop_request.clear()
                self.thread = gevent.spawn(self._process)

    def _process(self):
        for item in self._consume():
            if self._consumer.had_timeout:
                # If there was a timeout, skip over the emit.
                continue
            self.socket_io.emit(self.event, item, *self.args, **self.kwargs)

    def abort(self, timeout=None):
        with self.mutex:
            if self.thread and not self.thread.dead:
                self.stop_request.set()
                self.thread.join(timeout)
