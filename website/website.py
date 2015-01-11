from flask import Flask
from flask import render_template
from flask.ext.socketio import SocketIO
import news

app = Flask(__name__)
socket_io = SocketIO(app)
app.register_blueprint(news.newsBluePrint, url_prefix='/news')

@app.route('/')
def hello_world():
    return render_template("index.html")


if __name__ == '__main__':
    socket_io.run(app)
