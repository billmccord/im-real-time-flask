import threading
from time import strftime, sleep
from flask import Flask, render_template, Response, json
from flask.ext.socketio import SocketIO
from werkzeug._internal import _log
import news


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
    return Response(generate_news_stream(), mimetype="text/event-stream")


def generate_news_stream():
    news_count = 0
    while True:
        news_count += 1
        _log('info', 'Streaming news')
        yield 'data: %s\n\n' % json.dumps(generate_news(news_count))
        _log('info', 'Sleeping')
        sleep(5)
        _log('info', 'Woke up')


@socket_io.on('connect', namespace='/news')
def test_connect():
    emit_news(0)


def news_thread():
    news_count = 0
    while True:
        news_count += 1
        emit_news(news_count)
        _log('info', 'Sleeping')
        sleep(5)
        _log('info', 'Woke up')


def emit_news(news_count):
    _log('info', 'Generating news')
    new_news = generate_news(news_count)
    _log('info', 'Emitting news: %s' % new_news)
    socket_io.emit('new-news', new_news, namespace='/news')


def generate_news(news_count):
    return \
        {
            "content": "The content for the news story %d." % (++news_count),
            "date": strftime('%Y/%m/%d'),
            "headline": "News story %d" % news_count,
            "icon": "",
            "source": "Source %d" % news_count
        }

_log('info', 'Creating news thread')
t = threading.Thread(target=news_thread)
t.daemon = True
t.start()

if __name__ == '__main__':
    _log('info', 'Starting app')
    socket_io.run(app)