import os
import json
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt

# Ordner mit JSON-Dateien
folder_path = '/Users/hamzabartl/Documents/DataSciencePy/pythonProject/recorded-tweets'

# Alle JSON-Dateien im Ordner einlesen
all_tweets = []
file_count = 0
max_files = 600

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

# Die JSON-Daten in ein DataFrame umwandeln
df = pd.json_normalize(all_tweets, sep='_')

# Sicherstellen, dass die 'text'-Spalte vom Typ string ist und NaN-Werte in 'text' entfernen
df['text'] = df['text'].astype(str)
df = df.dropna(subset=['text'])

# Entfernen von Retweets
df = df[~df['text'].str.startswith('RT')]

# Extrahieren von Hashtags
def extract_hashtags(text):
    return re.findall(r'#(\w+)', text)

df['hashtags'] = df['text'].apply(extract_hashtags)

# Zählen der Häufigkeit der Hashtags
hashtags = Counter([hashtag for hashtags in df['hashtags'] for hashtag in hashtags])

# Die 10 häufigsten Hashtags visualisieren
common_hashtags = hashtags.most_common(10)
labels, values = zip(*common_hashtags)

plt.figure(figsize=(10, 6))
plt.bar(labels, values)
plt.xlabel('Hashtags')
plt.ylabel('Häufigkeit')
plt.title('Top 10 Hashtags')
plt.show()