from threading import Thread
from time import strftime, sleep
from flask import Flask
from flask import render_template
from flask.ext.socketio import SocketIO
from werkzeug._internal import _log
import news

app = Flask(__name__)
socket_io = SocketIO(app)
app.register_blueprint(news.newsBluePrint, url_prefix='/news')

@app.route('/')
def hello_world():
    return render_template("index.html")

@socket_io.on('connect', namespace='/news')
def test_connect():
    socket_io.emit('new-news', generate_news(0), namespace='/news')


class NewsEmitter(Thread):
    def run(self):
        news_count = 0
        while True:
            news_count += 1
            news = generate_news(news_count)
            _log('info', 'Emitting news: %s' % news)
            socket_io.emit('new-news', news, namespace='/news')
            _log('info', 'Sleeping')
            sleep(5)
            _log('info', 'Woke up')


def generate_news(news_count):
    return \
        {
            "content": "The content for the news story %d." % (++news_count),
            "date": strftime('%Y/%m/%d'),
            "headline": "News story %d" % news_count,
            "icon": "",
            "source": "Source %d" % news_count
        }

if __name__ == '__main__':
    _log('info', 'Starting news emitter')
    NewsEmitter().start()
    _log('info', 'Started news emitter')

    _log('info', 'Starting app')
    socket_io.run(app)