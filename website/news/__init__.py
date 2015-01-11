from flask import Blueprint, jsonify
from .news_service import NewsService

bp = Blueprint('news', __name__)
newsBluePrint = Blueprint('news', __name__)

@newsBluePrint.route('/api/News', methods=['GET'])
def News():
    return jsonify(NewsService().GetNews())
