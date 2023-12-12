import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import xgboost as xgb

url = 'http://192.168.0.142:3000/api/prices/AUDUSD/5'  # Příklad URL, upravte podle vašich potřeb
headers = {'Accept': 'application/json'}  # Případné hlavičky pro autentizaci

# Získání dat z API
response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception('Got unexpected response {}'.format(response.text))

print('Data requested', flush=True)

data = response.json()

# Převod dat na DataFrame
df = pd.DataFrame(data)
df.set_index('timestamp')
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df = df.set_index('timestamp')
train, test = train_test_split(df, test_size=0.3, random_state=42)

def create_feature(df):
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear

create_feature(df)
sns.boxplot(data=df, x='hour', y='close')
plt.show()