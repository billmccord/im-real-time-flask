import sys
# Remove threading so that monkey patching works correctly.
if 'threading' in sys.modules:
    del sys.modules['threading']
from gevent import monkey
# Use gevent instead of threading.
# http://www.gevent.org/intro.html
monkey.patch_all()

from flask import Flask, render_template, Response
from flask.ext.socketio import SocketIO


from producer import SimpleQueueProducer
from processor import SocketBroadcaster
from processor import SSEStreamer
from news import newsBluePrint
from generator import NewsGenerator

app = Flask(__name__)
socket_io = SocketIO(app)
app.register_blueprint(newsBluePrint, url_prefix='/news')
simple_producer = SimpleQueueProducer()
socket_broadcaster = SocketBroadcaster(socket_io, simple_producer, 'new-news',
                                       namespace='/news')
news_generator = NewsGenerator(simple_producer)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/news')
def news():
    return render_template("news.html")


@app.route('/news-stream')
def news_stream():
    headers = dict()
    headers['Access-Control-Allow-Origin'] = '*'
    # Always generate a unique producer and generator for SSEs.
    unique_producer = SimpleQueueProducer()
    unique_news_generator = NewsGenerator(unique_producer)
    unique_news_generator.generate()
    streamer = SSEStreamer(unique_producer)
    streamer.finished = streaming_finished
    streamer.aborted = streaming_aborted
    return Response(streamer.process(),
                    mimetype="text/event-stream",
                    headers=headers)


def streaming_finished():
    print "Streaming Finished"


def streaming_aborted():
    print "Streaming Aborted"


@socket_io.on('connect', namespace='/news')
def test_connect():
    # Reuse the same generator for broadcast events.
    news_generator.generate()
    socket_broadcaster.process()


if __name__ == '__main__':
    socket_io.run(app)