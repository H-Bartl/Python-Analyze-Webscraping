import os
import gzip
import json
import pandas as pd
import re
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

# Schriftart auf Standard zurücksetzen
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# Ordner mit JSON.GZ-Dateien
folder_path = '/Users/hamzabartl/Documents/DataSciencePy/pythonProject/7528718/german-tweet-sample-2019-04'

# Alle JSON.GZ-Dateien im Ordner einlesen
all_tweets = []

for filename in os.listdir(folder_path):
    if filename.endswith('.json.gz'):
        with gzip.open(os.path.join(folder_path, filename), 'rt', encoding='utf-8', errors='ignore') as file:
            try:
                json_data = json.load(file)
                all_tweets.extend(json_data)
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

# Filtern der Tweets, die den Hashtag #AfD enthalten
df_afd = df[df['hashtags'].apply(lambda x: 'AfD' in x)]

# Sicherstellen, dass die 'created_at'-Spalte als Datetime-Objekt behandelt wird
df_afd['created_at'] = pd.to_datetime(df_afd['created_at'])

# Filtern nach Tweets im April 2019
df_afd_april_2019 = df_afd[(df_afd['created_at'] >= '2019-04-01') & (df_afd['created_at'] < '2019-05-01')]

# Aggregieren der Daten nach Datum
df_afd_april_2019['date'] = df_afd_april_2019['created_at'].dt.date
afd_counts_april_2019 = df_afd_april_2019.groupby('date').size()

# Visualisieren der aggregierten Daten in einem Liniendiagramm
plt.figure(figsize=(12, 6))
afd_counts_april_2019.plot(kind='line', marker='o')
plt.xlabel('Datum')
plt.ylabel('Anzahl der Tweets')
plt.title('Anzahl der Tweets mit dem Hashtag #AfD im April 2019')
plt.grid(True)
plt.show()

# Finden des Tages mit den meisten Tweets
max_date = afd_counts_april_2019.idxmax()

# Filtern der Tweets an diesem Tag
df_max_date = df_afd_april_2019[df_afd_april_2019['date'] == max_date]

# Aggregieren der Daten nach Uhrzeit (auf Stundenebene)
df_max_date['hour'] = df_max_date['created_at'].dt.hour
afd_counts_hour = df_max_date.groupby('hour').size()

# Visualisieren der aggregierten Daten in einem Liniendiagramm
plt.figure(figsize=(12, 6))
afd_counts_hour.plot(kind='line', marker='o')
plt.xlabel('Uhrzeit')
plt.ylabel('Anzahl der Tweets')
plt.title(f'Anzahl der Tweets mit dem Hashtag #AfD am {max_date}')
plt.grid(True)
plt.xticks(range(0, 24, 2))  # Nur gerade Stunden anzeigen
plt.show()
