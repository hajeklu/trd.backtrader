import backtrader as bt
import yfinance as yf
import pandas as pd


class GoldenCrossStrategy(bt.Strategy):
    params = (
        ("short_term", 50),
        ("long_term", 200),
        ("order_percentage", 0.95),
    )

    def __init__(self):
        self.short_term_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.short_term
        )
        self.long_term_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.long_term
        )
        self.crossover = bt.indicators.CrossOver(
            self.short_term_ema, self.long_term_ema
        )

    def next(self):
        if self.crossover > 0:
            if not self.position:
                size = int((self.broker.get_cash() /
                           self.data.close[0]) * self.params.order_percentage)
                self.buy(size=size)
        elif self.crossover < 0:
            if self.position:
                self.sell(size=self.position.size)


if __name__ == '__main__':
    cerebro = bt.Cerebro(optreturn=False)

    # Add the strategy
    cerebro.optstrategy(
        GoldenCrossStrategy,
        # Test short term EMA periods from 1 to 200 in steps of 10
        short_term=range(1, 201, 10),
        # Test long term EMA periods from 1 to 200 in steps of 10
        long_term=range(1, 201, 10)
    )

    # Fetch the data from Yahoo Finance
    df = yf.download('AAPL', start='2020-01-01', end='2023-01-01')
    data = bt.feeds.PandasData(dataname=df)

    # Add the data to Cerebro
    cerebro.adddata(data)

    # Set the cash
    cerebro.broker.set_cash(10000)

    # Set the commission
    cerebro.broker.setcommission(commission=0.001)

    # Add a sizer
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    # Run the backtest
    results = cerebro.run(maxcpus=1)

    # Extract results
    final_results_list = []
    for run in results:
        for strategy in run:
            value = round(strategy.broker.get_value(), 2)
            short_term, long_term = strategy.params.short_term, strategy.params.long_term
            final_results_list.append((short_term, long_term, value))

    # Sort results list by end value
    by_end_value = sorted(final_results_list, key=lambda x: x[2], reverse=True)
    for result in by_end_value[:10]:  # Print top 10 results
        print("Short Term:", result[0], "Long Term:",
              result[1], "Final Value:", result[2])
