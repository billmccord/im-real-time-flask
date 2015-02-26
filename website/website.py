from flask import Flask, render_template, Response
from flask.ext.socketio import SocketIO
from gevent import monkey

from producer import SimpleQueueProducer
from processor import SocketBroadcaster
from processor import SSEStreamer
from news import newsBluePrint
from generator import NewsGenerator

# Make sockets use gevent:
# http://www.gevent.org/intro.html
monkey.patch_socket()

app = Flask(__name__)
socket_io = SocketIO(app)
app.register_blueprint(newsBluePrint, url_prefix='/news')
socket_broadcaster = None
simple_producer = SimpleQueueProducer()
news_generator = None


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
    refresh_news_producer()
    return Response(SSEStreamer(simple_producer).process(),
                    mimetype="text/event-stream",
                    headers=headers)


@socket_io.on('connect', namespace='/news')
def test_connect():
    global socket_broadcaster
    if socket_broadcaster is None or not socket_broadcaster.isAlive():
        refresh_news_producer()
        socket_broadcaster = SocketBroadcaster(
            socket_io, simple_producer, 'new-news', namespace='/news')
        socket_broadcaster.start()


def refresh_news_producer():
    global news_generator
    if news_generator is None or not news_generator.isAlive():
        news_generator = NewsGenerator(simple_producer)
        news_generator.start()


if __name__ == '__main__':
    socket_io.run(app)