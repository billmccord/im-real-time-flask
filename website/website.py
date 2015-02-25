from flask import Flask, render_template, Response
from flask.ext.socketio import SocketIO
from werkzeug._internal import _log
from producer import NewsProducer
from processor import SocketBroadcaster
from processor import SSEStreamer
from news import newsBluePrint

app = Flask(__name__)
socket_io = SocketIO(app)
app.register_blueprint(newsBluePrint, url_prefix='/news')
socket_broadcaster = None
news_producer = NewsProducer()
news_producer.start()


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
    return Response(SSEStreamer(news_producer).process(),
                    mimetype="text/event-stream",
                    headers=headers)


@socket_io.on('connect', namespace='/news')
def test_connect():
    global socket_broadcaster
    if socket_broadcaster is None or not socket_broadcaster.isAlive():
        socket_broadcaster = SocketBroadcaster(
            socket_io, news_producer, 'new-news', namespace='/news')
        socket_broadcaster.start()


if __name__ == '__main__':
    _log('info', 'Starting app')
    socket_io.run(app)