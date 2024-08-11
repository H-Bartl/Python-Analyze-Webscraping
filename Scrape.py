import requests
from bs4 import BeautifulSoup
import pandas as pd

archive_url = "https://web.archive.org/web/20190507094611/https://twitter.com/AfD"

response = requests.get(archive_url)
response.raise_for_status()  # Überprüfen, ob die Anfrage erfolgreich war

soup = BeautifulSoup(response.text, 'html.parser')

tweets = soup.find_all('div', {'class': 'tweet'})

tweets_list = []

for tweet in tweets:
    tweet_id = tweet['data-item-id']
    tweet_text = tweet.find('p', {'class': 'tweet-text'}).text if tweet.find('p', {'class': 'tweet-text'}) else ''
    tweet_date = tweet.find('a', {'class': 'tweet-timestamp'})['title'] if tweet.find('a', {'class': 'tweet-timestamp'}) else ''
    username = tweet['data-screen-name'] if 'data-screen-name' in tweet.attrs else ''
    tweets_list.append([tweet_date, tweet_id, tweet_text, username])

tweets_df = pd.DataFrame(tweets_list, columns=['date', 'id', 'content', 'username'])
print(tweets_df.head())
tweets_df.to_csv("archived_tweets_AfD_May4_2019.csv", index=False)
