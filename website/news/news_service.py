from .news_repository import NewsRepository

class NewsService(object):
    def GetNews(self):
        return NewsRepository().GetNews()
