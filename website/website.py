from flask import Flask, render_template, Response
from flask.ext.socketio import SocketIO
from werkzeug._internal import _log
import news
from news_producer import NewsProducer
from socket_broadcast_consumer import SocketBroadcastConsumer
from sse_consumer import SSEConsumer

app = Flask(__name__)
socket_io = SocketIO(app)
app.register_blueprint(news.newsBluePrint, url_prefix='/news')


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
    return Response(SSEConsumer(news_producer).consume(),
                    mimetype="text/event-stream",
                    headers=headers)


@socket_io.on('connect', namespace='/news')
def test_connect():
    if not socket_broadcast_consumer.isAlive():
        socket_broadcast_consumer.start()


news_producer = NewsProducer()
news_producer.start()
socket_broadcast_consumer = SocketBroadcastConsumer(socket_io, news_producer)

if __name__ == '__main__':
    _log('info', 'Starting app')
    socket_io.run(app)