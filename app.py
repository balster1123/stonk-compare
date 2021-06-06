import json
import typing

from flask import Flask, request

import stock_stats

app = Flask("stonk-compare")


@app.route("/heartbeat")
def hello():
    return "Hello World"


@app.route("/compare")
def stock_hist():
    query_params = request.args
    tickers = query_params.get("tickers", None)
    if tickers:
        tickers = tickers.split(",")
    period = query_params.get("period", "ytd")
    interval = query_params.get("interval", "1d")
    sort_tickers = bool(query_params.get("sort", 0))

    stock_hist = stock_stats.get_hist(tickers, period, interval, sort_tickers)
    return json.dumps([stat.to_dict() for stat in stock_hist])


if __name__ == '__main__':
    app.run()
