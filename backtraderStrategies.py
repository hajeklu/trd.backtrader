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


class TestStrategy(bt.Strategy):

    params = (
        ("EMA1", 20),  # Default value for EMA1
        ("EMA2", 80),  # Default value for EMA2
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt, txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
        self.previous_ema1 = None
        self.previous_ema2 = None
        self.orderProfit = None
        self.ema1_timeFrame = self.params.EMA1
        self.ema2_timeFrame = self.params.EMA2
        self.ema1 = bt.indicators.ExponentialMovingAverage(
            self.datas[0], period=self.params.EMA1)
        self.ema2 = bt.indicators.ExponentialMovingAverage(
            self.datas[0], period=self.params.EMA2)
        self.profitable_orders = 0
        self.loss_orders = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            self.bar_executed = len(self)

    def next(self):
        if (not hasattr(self, 'ema2')):
            return

        if self.position:
            self.closeOrderLogic()
        else:
            self.openOrderLogic()
            pass

    def closeOrderLogic(self):
        if self.order:
            if self.getOrderProfit() < self.orderProfit:
                if self.getOrderProfit() > 0:
                    self.profitable_orders += 1
                else:
                    self.loss_orders += 1
                self.close()
                self.order = None
                self.orderProfit = 0
            else:
                self.orderProfit = self.getOrderProfit()

    def openOrderLogic(self):
        if (self.previous_ema1 is None or self.previous_ema2 is None):
            self.previous_ema1 = self.ema1[0]
            self.previous_ema2 = self.ema2[0]
            return

        ema_1 = self.ema1[0]
        ema_2 = self.ema2[0]

        if self.previous_ema1 >= self.previous_ema2 and ema_1 < ema_2:
            self.order = self.sell()
        if self.previous_ema1 <= self.previous_ema2 and ema_1 > ema_2:
            self.order = self.buy()

        self.previous_ema1 = ema_1
        self.previous_ema2 = ema_2
        self.orderProfit = 0

    def getOrderProfit(self):
        if self.order.isbuy():
            return self.data.close[0] - self.order.executed.price
        else:
            return self.order.executed.price - self.data.close[0]

    def getStatistics(self):
        return {
            'profitableOrders': self.profitable_orders,
            'lossOrders': self.loss_orders
        }
