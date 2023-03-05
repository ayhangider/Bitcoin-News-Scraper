from textblob import TextBlob
from wordcloud import WordCloud
import numpy as np
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import timedelta

def sentiment_Vader_DESC(text):
    over_all_polarity=SentimentIntensityAnalyzer().polarity_scores(text)
    return over_all_polarity

def grouped_compound(comp):
    if comp >= 0.05:
        return "positive"
    elif comp<=-0.05:
        return "negative"
    else:
        return "neutral"


x = 1
news_list = []  #### HABER LİNKLERİ
while x < 5:

    page = f'https://news.bitcoin.com/page/{x}/'
    # print(page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
    r = requests.get(page, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    atags = soup.find_all('a')
    spaces = soup.find_all('a', {'class': 'story--medium__img-container'})
    for a in spaces:
        a = str(a).split('href="')[1].split('/">')[0]
        news_list.append(a)
    x += 1

#### HABER İÇERİKLERİ
data = pd.DataFrame(columns=['New_Date', 'Lean_Date', 'Lean_New_Hour', 'Lean_New_DateTime', 'New_Article'])
for page in news_list:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
    r = requests.get(page, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    ptags = soup.find_all('p')
    meta = soup.find('meta', {'property': 'article:published_time'})
    datetime_now = datetime.now()
    new_datetime = str(meta).split('content="')[1].split('" property=')[0]
    new_datetime = (datetime.fromisoformat(new_datetime))
    lean_new_date = new_datetime.date()
    lean_new_hour = new_datetime.hour
    lean_new_datetime = str(new_datetime.date()) + (' ') + str(new_datetime.hour) + (':00:00')
    lean_new_datetime = datetime.strptime(lean_new_datetime, "%Y-%m-%d %H:%M:%S")

    text = [paragraph.text for paragraph in ptags]
    words = ' '.join(text).split(' ')
    ARTICLE = ' '.join(words)
    ARTICLE = re.sub("\n", "", ARTICLE)
    ARTICLE = re.sub('#[A-Za-z0-9]+', '', ARTICLE)  # removes any strings with a '#'
    ARTICLE = re.sub('\\n', '', ARTICLE)  # removing the '\n' string
    ARTICLE = re.sub('https?:\/\/\S+', '', ARTICLE)  # removes any hyperlinks
    try:
        ARTICLE = ARTICLE.split('by')[1]
    except:
        continue
    new_dict = {'New_Date': new_datetime,
                'Lean_Date': lean_new_date,
                'Lean_New_Hour': lean_new_hour,
                'Lean_New_DateTime': lean_new_datetime,
                'New_Article': ARTICLE
                }
    data = data.append(new_dict, ignore_index=True)
    print(page)
btc_news = data.copy()
btc_news = btc_news.drop(columns=['New_Date', 'Lean_Date', 'Lean_New_Hour'])

#### HABER DUYGU SKORLARI

lists = data['New_Article'].apply(lambda x: sentiment_Vader_DESC(x))
Negativity = []
Neutral = []
Positivity = []
Compound = []
Sentiment_conc = []
count = 0
while count < len(lists):
    neg, neut, post, comp = lists[count].values()
    print(count)
    Negativity.append(neg)
    Neutral.append(neut)
    Positivity.append(post)
    Compound.append(comp)
    if comp >= 0.05:
        Sentiment_conc.append("positive")
    elif comp <= -0.05:
        Sentiment_conc.append("negative")
    else:
        Sentiment_conc.append("neutral")
    count += 1
btc_news['Negativity'] = Negativity
btc_news['Neutral'] = Neutral
btc_news['Positivity'] = Positivity
btc_news['Compound'] = Compound
btc_news['Sentiment_Conc'] = Sentiment_conc
btc_news = btc_news.groupby('Lean_New_DateTime').agg(News_Compound_mean=('Compound', 'mean'))
btc_news = btc_news.reset_index()
btc_news['Date'] = btc_news['Lean_New_DateTime']
btc_news = btc_news.drop('Lean_New_DateTime', axis=1)
btc_news['sentimentOfNews'] = btc_news.News_Compound_mean.apply(grouped_compound)
