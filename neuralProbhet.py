import requests
import pandas as pd
from neuralprophet import NeuralProphet
import plotly.offline as py_offline
from multiprocessing import Process    
import time 

symbolsToAnalysts = ['EURGBP', 'USDCAD', 'AUDUSD', 'EURUSD', 'USDJPY', 'GBPUSD', 'EURJPY',
                     'EURCHF', 'GBPJPY', 'GBPCHF', 'USDCHF', 'NZDUSD', 'CADJPY', 'GBPCAD',
                     'NZDCAD', 'AUDJPY', 'EURNOK', 'AUDCAD', 'EURNZD', 'EURCNH', 'NZDCHF',
                     'GBPNZD', 'EURCAD', 'AUDCHF', 'AUDNZD', 'EURAUD', 'GBPAUD', 'USDNOK',
                     'USDCNH', 'USDSEK', 'CHFJPY', 'EURSEK', 'CADCHF', 'BITCOIN']

def fetch_data(url, symbol, interval):
    response = requests.get(url, json={"symbol": symbol, "interval": interval})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data: {response.status_code}")


def predict(symbol, interval = 1440):
  while True:
        api_url = f'http://192.168.0.236:3000/api/prices/{symbol}/{interval}'

        # Fetching data
        data = fetch_data(api_url, symbol, interval)  # Assuming '1' is the interval

        # Converting data to pandas DataFrame
        df = pd.DataFrame(data)
        df['ds'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['y'] = df['close']
        df = df[['ds', 'y']]  # Keeping only 'ds' and 'y' columns
        df.set_index('ds', inplace=True)
        df = df.resample('H').interpolate(method='linear')
        df.reset_index(inplace=True)

        # Training the model
        model = NeuralProphet(n_lags=24, quantiles=[0.05, 0.95])
        model.fit(df, freq='H')

        # Making a future dataframe for 1 future period
        future_periods = model.make_future_dataframe(df, periods=1)

        # Predicting the future
        forecast_future = model.predict(future_periods)
        print(forecast_future.tail())

        # Extracting the last prediction
        last_prediction = forecast_future.iloc[-1]

        print(last_prediction)
        post_data = {
            "timestamp": last_prediction['ds'].strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "yhat": last_prediction['yhat1'],
            "yhat05": last_prediction['yhat1 5.0%'],
            "yhat95": last_prediction['yhat1 95.0%'],
        }
        # URL for your POST endpoint
        post_url = 'http://localhost:3001/api/prediction'

        # Making the POST request
        response = requests.post(post_url, json=post_data)

        # Checking the response
        if response.status_code == 200:
            print('Prediction successfully sent!')
        else:
            print(f'Error sending prediction: {response.status_code} - {response.text}')
        time.sleep(1200)
        

if __name__ == "__main__":
    for symbol in symbolsToAnalysts:
        Process(target=predict, args=(symbol,)).start()
