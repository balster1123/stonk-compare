import itertools
import json
import typing
from dataclasses import dataclass

import scipy.stats
import yfinance as yf
import requests_cache

DEFAULT_TICKERS = ["GME", "AMC"]
PERIOD_OPTIONS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
INTERVAL_OPTIONS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]


@dataclass
class StockLinearStats:
    r_squared: float
    p_value: float

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "r_squared": self.r_squared,
            "p_value": self.p_value
        }


STAT_NAMES = ["Open", "Close", "Low", "High", "Volume"]


@dataclass
class StockComparison:
    ticker1: str
    ticker2: str
    open_stats: typing.Optional[StockLinearStats] = None
    close_stats: typing.Optional[StockLinearStats] = None
    low_stats: typing.Optional[StockLinearStats] = None
    high_stats: typing.Optional[StockLinearStats] = None
    volume_stats: typing.Optional[StockLinearStats] = None

    @property
    def key(self):
        return f"{self.ticker1}-{self.ticker2}"

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "ticker1": self.ticker1,
            "ticker2": self.ticker2,
            "key": self.key,
            "open_stats": self.open_stats.to_dict(),
            "close_stats": self.close_stats.to_dict(),
            "low_stats": self.low_stats.to_dict(),
            "high_stats": self.high_stats.to_dict(),
            "volume_stats": self.volume_stats.to_dict(),
        }

    def calc_stats(self, history):
        self.open_stats = self._calc_stats(history["Open"])
        self.close_stats = self._calc_stats(history["Close"])
        self.low_stats = self._calc_stats(history["Low"])
        self.high_stats = self._calc_stats(history["High"])
        self.volume_stats = self._calc_stats(history["Volume"])

    def _calc_stats(self, measure_history):
        linear_regression = scipy.stats.linregress(x=measure_history[self.ticker1],
                                                   y=measure_history[self.ticker2])
        return StockLinearStats(
            r_squared=linear_regression.rvalue ** 2,
            p_value=linear_regression.pvalue,
        )


def get_hist(tickers: typing.List[str] = None, period: str = "ytd", interval: str = "1d", sort_tickers=False):
    if not tickers:
        tickers = DEFAULT_TICKERS

    if sort_tickers:
        tickers = sorted(tickers)

    session = requests_cache.CachedSession("yfinance.cache")
    session.headers['User-agent'] = 'stonk-compare/1.0'
    history = yf.download(tickers, period=period, interval=interval)

    stats = []
    for ticker1, ticker2 in get_ticker_pairs(tickers):
        comparison = StockComparison(ticker1, ticker2)
        comparison.calc_stats(history)
        stats.append(comparison)

    return stats


def get_ticker_pairs(ticker_names):
    return itertools.combinations(ticker_names, 2)


if __name__ == '__main__':
    print(get_hist(["GME", "AMC", "AMZN", "NOK", "BB", "TSLA", "SPY"], "1mo", "1d"))
