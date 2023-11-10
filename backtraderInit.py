import backtrader as bt
import backtrader.feeds as btfeeds
import csv
import requests
import copy
from multiprocessing import Process
from datetime import datetime
from backtraderStrategies import TestStrategy, CustomAnalyzer

class Result:
    def __init__(self, ema, profit, profitableOrders, lossOrders):
        self.ema = ema
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
            print('Data requested for ' + self.p.symbol)
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
    

def analyzeSymbol(symbol):
    results = []
    for ema2 in range(1, 201):
        for ema1 in range(1, ema2):
            crebro = bt.Cerebro()

            START_CASH = 1000.0

            crebro.broker.setcash(START_CASH)

            data = RESTAPIData(
                url=f'http://192.168.0.142:3000/api/prices/{symbol}/1',
                headers={'Accept': 'application/json'},  # Add any necessary headers here
                symbol=symbol,
            )

            crebro.adddata(data)
            crebro.addsizer(bt.sizers.FixedSize, stake=10)
            crebro.broker.setcommission(
                commission=.00001)
            crebro.addanalyzer(CustomAnalyzer, _name='myresults')
            crebro.addstrategy(TestStrategy, EMA1=ema1, EMA2=ema2, symbol=symbol)

            # print('Starting Portfolio Value: %.10f' % crebro.broker.getvalue())

            analyzer_results = crebro.run()
            analysis = analyzer_results[0].analyzers.myresults.get_analysis()
            profitableOrders = analysis['profitableOrders']
            lossOrders = analysis['lossOrders']

            # print('Final Portfolio Value: %.10f' % crebro.broker.getvalue())
            FINAL_CASH = crebro.broker.getvalue()
            profit = FINAL_CASH - START_CASH
            print(f'EMA {symbol}: {ema1}/{ema2}, Profit: {profit}, orders: {profitableOrders}/{lossOrders}', flush=True)

            if profitableOrders > lossOrders and profit > 0:
                result = Result(str(ema1) + '/' + str(ema2),
                                  profit, profitableOrders, lossOrders)
                results.append(result)
                csv_file_path = f'{symbol}_profits.csv'
                with open(csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    
                    if (file.tell() == 0):
                        writer.writerow(["EMA", "Profit", "Profitable Orders", "Loss Orders"])
                    
                    writer.writerow([result.ema, result.profit, result.profitableOrders, result.lossOrders])



for symbol in symbolsToAnalysts:
    if __name__ == '__main__':
        Process(target=analyzeSymbol, args=(symbol,)).start()
        #analyzeSymbol(symbol)


