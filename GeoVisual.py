import os
import gzip
import json
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import folium
import plotly.express as px
import warnings

# Unterdrücken der Warnung
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

# Extrahieren der geografischen Informationen
def extract_coordinates(tweet):
    if isinstance(tweet.get('coordinates'), dict) and 'coordinates' in tweet['coordinates']:
        return tweet['coordinates']['coordinates']
    elif isinstance(tweet.get('place'), dict) and 'bounding_box' in tweet['place']:
        bbox = tweet['place']['bounding_box']['coordinates'][0]
        # Berechnen des Mittelpunkts des Bounding Box
        lon = sum([coord[0] for coord in bbox]) / len(bbox)
        lat = sum([coord[1] for coord in bbox]) / len(bbox)
        return [lon, lat]
    return None

df['coordinates'] = df.apply(extract_coordinates, axis=1)

# Überprüfen der Koordinaten
print(f"Anzahl der Tweets: {len(df)}")
print(f"Anzahl der Tweets mit Koordinaten: {df['coordinates'].notna().sum()}")

# Weiterverarbeitung nur, wenn Koordinaten vorhanden sind
if df['coordinates'].notna().sum() > 0:
    df = df.dropna(subset=['coordinates'])

    # Mittelpunkt der Karte (zum Beispiel)
    map_center = [51.1657, 10.4515]  # Deutschland

    # Erstellen einer Folium-Karte
    mymap = folium.Map(location=map_center, zoom_start=6)

    # Hinzufügen von Tweet-Standorten zur Karte
    for idx, row in df.iterrows():
        folium.Marker(location=[row['coordinates'][1], row['coordinates'][0]],
                      popup=row['text']).add_to(mymap)

    # Speichern der Karte als HTML-Datei
    mymap.save('tweets_map.html')

    # DataFrame vorbereiten für Plotly
    df['longitude'] = df['coordinates'].apply(lambda x: x[0])
    df['latitude'] = df['coordinates'].apply(lambda x: x[1])

    # Erstellen einer Plotly-Karte
    fig = px.scatter_geo(df, lat='latitude', lon='longitude',
                         hover_name='text', projection='natural earth')

    # Anzeigen der Karte
    fig.show()
else:
    print("Keine Koordinaten gefunden.")
