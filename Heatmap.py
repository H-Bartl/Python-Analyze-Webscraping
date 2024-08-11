import os
import gzip
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Reset font to default
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# Folder with JSON files
folder_path = '/Users/hamzabartl/Documents/DataSciencePy/pythonProject/7528718/german-tweet-sample-2019-04'

# Reading all JSON files
all_tweets = []

for filename in os.listdir(folder_path):
    if filename.endswith('.json.gz'):
        with gzip.open(os.path.join(folder_path, filename), 'rt', encoding='utf-8', errors='ignore') as file:
            try:
                json_data = json.load(file)
                all_tweets.extend(json_data)
            except json.JSONDecodeError:
                print(f"Fehler beim Lesen der Datei: {filename}")

# Converting JSON data to DataFrame
df = pd.json_normalize(all_tweets, sep='_')

# Ensure the 'text' column is of type string and remove NaNs in 'text'
df['text'] = df['text'].astype(str)
df = df.dropna(subset=['text'])

# Remove rts
df = df[~df['text'].str.startswith('RT')]

# Ensure the 'created_at' column is treated as datetime
df['created_at'] = pd.to_datetime(df['created_at'])

# Extract hour and weekday
df['hour'] = df['created_at'].dt.hour
df['weekday'] = df['created_at'].dt.dayofweek

# Aggregate data by hour and weekday
heatmap_data = df.groupby(['weekday', 'hour']).size().unstack(fill_value=0)

# Creating the heatmap
plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap='YlGnBu', linewidths=.5)
plt.xlabel('Stunde des Tages')
plt.ylabel('Wochentag')
plt.title('Twitter-Aktivität zu verschiedenen Tageszeiten und Wochentagen')
plt.yticks([0, 1, 2, 3, 4, 5, 6], ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'], rotation=0)
plt.show()
