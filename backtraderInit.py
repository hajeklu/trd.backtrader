import backtrader as bt
import backtrader.feeds as btfeeds
import csv
import requests
import copy
import pika
import json
from multiprocessing import Process    
from datetime import datetime
from datetime import datetime
from backtraderStrategies import TestStrategy, CustomAnalyzer


BASE_IP = 'http://192.168.0.142'
TRD_DATA_PROVIDER_URL = f'{BASE_IP}:3000'
TRD_FACE_ULR = f'{BASE_IP}:3001'
TIME_FRAME_COMPUTE_IN_MINUTES_DEFAULT = 5

class Result:
    def __init__(self,symbol, ema1, ema2, profit, profitableOrders, lossOrders):
        self.symbol = symbol
        self.ema1 = ema1
        self.ema2 = ema2
        self.profit = profit
        self.profitableOrders = profitableOrders
        self.lossOrders = lossOrders

data_cache = dict()
class RESTAPIData(bt.feed.DataBase):
    params = (
        ('url', ''),
        ('timeframe', 1),
        ('headers', {}),
        ('symbol', None),
    )

    def __init__(self):
        super(RESTAPIData, self).__init__()

    def start(self):
        super(RESTAPIData, self).start()
        global data_cache
        if data_cache.get(self.p.symbol) == None:
            response = requests.get(self.p.url, headers=self.p.headers)
            if response.status_code != 200:
                raise Exception('Got unexpected response {}'.format(response.text))
            print('Data requested for ' + self.p.symbol, flush=True)
            data = response.json()
            self.data = copy.deepcopy(data)
            data_cache[self.p.symbol] = copy.deepcopy(data)
        else:
            self.data = copy.deepcopy(data_cache.get(self.p.symbol))

    def _load(self):
        if not self.data:
            return False

        item = self.data.pop(0)
        self.lines.datetime[0] = bt.date2num(datetime.fromtimestamp(item['timestamp'] / 1000))
        self.lines.open[0] = item['open']
        self.lines.high[0] = item['high']
        self.lines.low[0] = item['low']
        self.lines.close[0] = item['close']
        self.lines.volume[0] = item['volume']

        return True



symbolsToAnalysts = ['EURGBP', 'USDCAD', 'AUDUSD', 'EURUSD', 'USDJPY', 'GBPUSD', 'EURJPY',
                     'EURCHF', 'GBPJPY', 'GBPCHF', 'USDCHF', 'NZDUSD', 'CADJPY', 'GBPCAD',
                     'NZDCAD', 'AUDJPY', 'EURNOK', 'AUDCAD', 'EURNZD', 'EURCNH', 'NZDCHF',
                     'GBPNZD', 'EURCAD', 'AUDCHF', 'AUDNZD', 'EURAUD', 'GBPAUD', 'USDNOK',
                     'USDCNH', 'USDSEK', 'CHFJPY', 'EURSEK', 'CADCHF']

def analyzeSymbol(symbol, timeFrame):
    result = None
    for ema2 in range(1, 201):
        for ema1 in range(1, ema2):
            crebro = bt.Cerebro()

            START_CASH = 1000.0

            crebro.broker.setcash(START_CASH)

            data = RESTAPIData(
                url=f'{TRD_DATA_PROVIDER_URL}/api/prices/{symbol}/{timeFrame}',
                headers={'Accept': 'application/json'},  # Add any necessary headers here
                symbol=symbol,
            )

            crebro.adddata(data)
            crebro.addsizer(bt.sizers.FixedSize, stake=100)
            crebro.addanalyzer(CustomAnalyzer, _name='myresults')
            crebro.addstrategy(TestStrategy, EMA1=ema1, EMA2=ema2, symbol=symbol)

            analyzer_results = crebro.run()
            analysis = analyzer_results[0].analyzers.myresults.get_analysis()
            profitableOrders = analysis['profitableOrders']
            lossOrders = analysis['lossOrders']

            print(f'EMA {ema1}/{ema2} orders: {profitableOrders}/{lossOrders}', flush=True)
            FINAL_CASH = crebro.broker.getvalue()
            profit = FINAL_CASH - START_CASH
            if profitableOrders > lossOrders and profit > 0:
                aspirant = Result(symbol, ema1, ema2, profit, profitableOrders, lossOrders)
                #sentResultsToRabbitMQ(aspirant, True)
                if result == None:
                    result = aspirant
                
                if aspirant.profit > result.profit:
                       result = aspirant
        # print(f'Progress {symbol} - {ema2}', flush=True)
    if result == None: 
        result = Result(symbol, 0, 0, 0, 0, 0)
    
    #sentResults(result)
    #sentResultsToRabbitMQ(result)
    if result.ema1 != 0 and result.ema2 != 0:
        print(f'Result {symbol} at {result.ema1} / {result.ema2} orders: {result.lossOrders} / {result.profitableOrders}', flush=True)
    
def sentResults(result):
    data_to_send = {"symbol": result.symbol, "ema1": result.ema1, "ema2": result.ema2}

    # API endpoint URL
    url = f'{TRD_FACE_ULR}/api/ema'
    # Make the POST request
    response = requests.post(url, json=data_to_send)

    # Check the response
    if response.status_code != 201:
        print("Error:", response.status_code, response.text)
  
def sentResultsToRabbitMQ(result, isAspirant = False):
    data_to_send = {"symbol": result.symbol, "ema1": result.ema1, "ema2": result.ema2, "profit": result.profit, "profitableOrders": result.profitableOrders, "lossOrders": result.lossOrders, "isAspirant": isAspirant, "timeFrame": TIME_FRAME_COMPUTE_IN_MINUTES_DEFAULT}
    try:
        # Setup RabbitMQ connection and channel
        connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.142')) # Update the host if RabbitMQ is not on localhost
        channel = connection.channel()
        topicName = f'Results_{TIME_FRAME_COMPUTE_IN_MINUTES_DEFAULT}'
        # Declare a queue (if it doesn't exist, it will be created)
        channel.queue_declare(queue=topicName, durable=True) # Replace with your queue name

        # Publish the message
        channel.basic_publish(exchange='', routing_key=topicName, body=json.dumps(data_to_send))

    except Exception as e:
        print("RabbitMQ Error:", str(e))
    finally:
        if connection:
            connection.close()
            
if __name__ == "__main__":
    for symbol in symbolsToAnalysts:
        #Process(target=analyzeSymbol, args=(symbol, TIME_FRAME_COMPUTE_IN_MINUTES_DEFAULT)).start()
        analyzeSymbol(symbol, TIME_FRAME_COMPUTE_IN_MINUTES_DEFAULT)