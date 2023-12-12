import requests
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from pmdarima.arima import auto_arima

def ad_test(dataset):
    dftest = adfuller(dataset, autolag='AIC')
    print("1. ADF : ", dftest[0])
    print("2. P-Value : ", dftest[1])
    print("3. Num Of Lags : ", dftest[2])
    print("4. Num Of Observations Used For ADF Regression:", dftest[3])
    print("5. Critical Values :")
    for key, val in dftest[4].items():
        print("\t", key, ": ", val)
    if dftest[0] < dftest[4]["5%"]:
        print("=> Data is stationary")
    else:
        print("=> Data is non-stationary")

# Definujte URL a hlavičky pro vaše API
url = 'http://192.168.0.142:3000/api/prices/EURUSD/60'  # Příklad URL, upravte podle vašich potřeb
headers = {'Accept': 'application/json'}  # Případné hlavičky pro autentizaci

# Získání dat z API
response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception('Got unexpected response {}'.format(response.text))

print('Data requested', flush=True)
data = response.json()

# Převod dat na DataFrame
df = pd.DataFrame(data)

# Převedení časového razítka na čitelný formát a nastavení jako indexu
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Nastavení frekvence časových údajů na 5 minut
df = df.asfreq(pd.Timedelta(minutes=5))

# Vyberte sloupec 'close' pro modelování
time_series = df['close']
time_series = time_series.dropna()
ad_test(time_series)


# První diferencování
diff_data = time_series.diff().dropna()

# Provedení Dickey-Fullerova testu na diferencované časové řadě
ad_test(diff_data)



# Modelování ARIMA
stepwise_fit = auto_arima(time_series, trace=True, suppress_warnings=True)

# Předpovědi
predictions = model_fit.forecast(steps=5)  # Předpovědi pro následujících 5 kroků
print(predictions)
