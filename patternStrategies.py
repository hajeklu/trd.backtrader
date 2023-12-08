# Import the backtrader platform
import backtrader as bt

class CustomAnalyzer(bt.Analyzer):
    def start(self):
        self.profitableOrders = None
        self.lossOrders = None

    def stop(self):
        # Save whatever values you want from the strategy
        # Let's say you've defined a method called return_value
        self.strat_return = self.strategy.getStatistics()

    def get_analysis(self):
        return {
            'profitableOrders': self.strat_return['profitableOrders'],
            'lossOrders': self.strat_return['lossOrders'],
        }


class PatternStrategy(bt.Strategy):

    params = (
        ("symbol", "EURUSD")
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt, txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
        self.orderProfit = None
        self.symbol = self.params.symbol
        self.profitable_orders = 0
        self.loss_orders = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            self.bar_executed = len(self)

    def next(self):
        
        if self.position:
            self.closeOrderLogic()
        else:
            self.openOrderLogic()
            pass

    def closeOrderLogic(self):


    def openOrderLogic(self):


    def getOrderProfit(self):
        if self.order.isbuy():
            return self.data.close[0] - (self.order.executed.price + self.getPip(self.symbol))
        else:
            return self.order.executed.price - (self.data.close[0] + self.getPip(self.symbol))

    def getStatistics(self):
        return {
            'profitableOrders': self.profitable_orders,
            'lossOrders': self.loss_orders
        }
    # example self, EURUSD, 1.12345
    def getPip(self, symbol): 
        is_jpy_pair = 'JPY' in symbol.upper()
        # Set the pip value based on whether it's a JPY pair
        pip_value = 0.01 if is_jpy_pair else 0.0001
        return pip_value