class NewsRepository(object):
    def GetNews(self):
        return {
            "news": [
                {
                    "content": "The content for the news story 1.",
                    "date": "2014/01/01",
                    "headline": "The first news story",
                    "icon": "",
                    "source": "Source 1"
                },
                {
                    "content": "The content for the news story 2.",
                    "date": "2014/02/01",
                    "headline": "The second news story",
                    "icon": "",
                    "source": "Source 2"
                }
            ]
        }