import os
import json
import pandas as pd
import re
from textblob import TextBlob
import matplotlib.pyplot as plt

# Folder with JSON files
folder_path = '/Users/hamzabartl/Documents/DataSciencePy/pythonProject/recorded-tweets'

# Reading all JSON files
all_tweets = []
file_count = 0
max_files = 500

for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8', errors='ignore') as file:
            try:
                json_data = json.load(file)
                all_tweets.extend(json_data)
                file_count += 1
                if file_count >= max_files:
                    break
            except json.JSONDecodeError:
                print(f"Fehler beim Lesen der Datei: {filename}")

df = pd.json_normalize(all_tweets, sep='_')

df['text'] = df['text'].astype(str)
df = df.dropna(subset=['text'])

df = df[~df['text'].str.startswith('RT')]

# Text bereinigen
def clean_tweet(text):
    text = re.sub(r'http\S+', '', text)  # Entfernen von URLs
    text = re.sub(r'@\w+', '', text)     # Entfernen von @-Erwähnungen
    text = re.sub(r'#\w+', '', text)     # Entfernen von Hashtags
    text = re.sub(r'\s+', ' ', text).strip()  # Entfernen von überflüssigen Leerzeichen
    return text

df['cleaned_text'] = df['text'].apply(clean_tweet)

def extract_hashtags(text):
    return re.findall(r'#(\w+)', text)

df['hashtags'] = df['text'].apply(extract_hashtags)

def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity < 0:
        return 'negative'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'

df['sentiment'] = df['cleaned_text'].apply(get_sentiment)

def sentiment_for_hashtags(df, hashtags):
    hashtag_sentiments = {}
    for hashtag in hashtags:
        df_hashtag = df[df['hashtags'].apply(lambda x: hashtag in x)]
        if not df_hashtag.empty:
            sentiment_counts = df_hashtag['sentiment'].value_counts()
            hashtag_sentiments[hashtag] = sentiment_counts
    return hashtag_sentiments

hashtags_to_analyze = ['AFD']

hashtag_sentiments = sentiment_for_hashtags(df, hashtags_to_analyze)

for hashtag, sentiment_counts in hashtag_sentiments.items():
    plt.figure(figsize=(8, 6))
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title(f'Stimmungsverteilung für #{hashtag}')
    plt.axis('equal')
    plt.show()
