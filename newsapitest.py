from newsapi import NewsApiClient
import json

# Init
newsapi = NewsApiClient(api_key='a58184c8b6014a9ea17772a36ff15f01')

# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(language='en')
resp = list(top_headlines['articles'])
news = ""

for i in range(5):
    news = news + str(i + 1) + " " + resp[i]['title'] + '\n'

print(news)