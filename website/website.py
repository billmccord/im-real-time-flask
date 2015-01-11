from flask import Flask
from flask import render_template
import news

app = Flask(__name__)
app.register_blueprint(news.newsBluePrint, url_prefix='/news')

@app.route('/')
def hello_world():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
