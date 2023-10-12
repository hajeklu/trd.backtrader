import backtrader as bt
import backtrader.feeds as btfeeds
import csv
from datetime import datetime
from backtraderStrategies import TestStrategy, CustomAnalyzer


class Result:
    def __init__(self, ema, profit, profitableOrders, lossOrders):
        self.ema = ema
        self.profit = profit
        self.profitableOrders = profitableOrders
        self.lossOrders = lossOrders


symbolsToAnalysts = ['EURGBP', 'USDCAD', 'AUDUSD', 'EURUSD', 'USDJPY', 'GBPUSD', 'EURJPY',
                     'EURCHF', 'GBPJPY', 'GBPCHF', 'USDCHF', 'NZDUSD', 'CADJPY', 'GBPCAD',
                     'NZDCAD', 'AUDJPY', 'EURNOK', 'AUDCAD', 'EURNZD', 'EURCNH', 'NZDCHF',
                     'GBPNZD', 'EURCAD', 'AUDCHF', 'AUDNZD', 'EURAUD', 'GBPAUD', 'USDNOK',
                     'USDCNH', 'USDSEK', 'CHFJPY', 'EURSEK', 'CADCHF', 'DE30', 'US100', 'EU50', 'UK100']
timeFrame = [1]

results = []

for symbol in symbolsToAnalysts:
    for tf in timeFrame:
        for ema2 in range(1, 201):
            for ema1 in range(1, ema2):
                crebro = bt.Cerebro()

                START_CASH = 1000.0

                crebro.broker.setcash(START_CASH)

                data = btfeeds.GenericCSVData(
                    dataname=f'normalized/{symbol}_{tf}_normalized.csv',
                    nullvalue=0.0,

                    dtformat=('%d/%m/%Y %H:%M:%S'),
                    timeframe=bt.TimeFrame.Minutes,
                    compression=1,

                    open=0,
                    high=1,
                    low=2,
                    close=3,
                    datetime=4,

                    volume=-1,
                    openinterest=-1
                )

                crebro.adddata(data)
                crebro.addsizer(bt.sizers.FixedSize, stake=10)
                crebro.broker.setcommission(
                    commission=.00001)
                crebro.addanalyzer(CustomAnalyzer, _name='myresults')
                crebro.addstrategy(TestStrategy, EMA1=ema1, EMA2=ema2)

                # print('Starting Portfolio Value: %.10f' % crebro.broker.getvalue())

                results = crebro.run()
                analysis = results[0].analyzers.myresults.get_analysis()
                profitableOrders = analysis['profitableOrders']
                lossOrders = analysis['lossOrders']

                # print('Final Portfolio Value: %.10f' % crebro.broker.getvalue())
                FINAL_CASH = crebro.broker.getvalue()
                profit = FINAL_CASH - START_CASH
                print(
                    f'EMA {symbol}_{tf}: {ema1}/{ema2}, Profit: {profit}, orders: {profitableOrders}/{lossOrders}')
                results.append(Result(str(ema1) + '/' + str(ema2),
                               profit, profitableOrders, lossOrders))

        results.sort(key=lambda x: x.profit, reverse=True)
        for stock in results[:10]:
            print(f"EMA: {stock.ema}, Profit: {stock.profit}")

        # Specify the CSV file path
        csv_file_path = f'{symbol}_{tf}_profits.csv'

        # Open the CSV file for writing
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header row
            writer.writerow(
                ["EMA", "Profit", "Profitable Orders", "Loss Orders"])

            # Write the data rows
            for result in results:
                writer.writerow([result.ema, result.profit,
                                result.profitableOrders, result.lossOrders])

        print(f"Profits saved to '{csv_file_path}' file.")
