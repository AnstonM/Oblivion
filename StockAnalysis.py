import yfinance as yf
import pandas as pd
import pandas_ta as ta
import config
import Messages
import talib
from enum import Enum

def checkSymbolExists(symbol: str):
    symbol = symbol.strip()
    try:
        yf.Ticker(f"{symbol}.NS").info["currentPrice"]
    except: 
        return False
    return True

def performAnalysis():
    with open("./MonitoringLists/1554223395.txt", "r") as monitoring_file:
        for i in monitoring_file.readlines():
            symbol = i.strip()
            print(
                yf.Ticker(f"{symbol}.NS")
                .history(period="1mo")
                .ta.cdl_pattern(name=all)
            )


def getStockDetails(symbol: str):
    symbol = symbol.strip()
    info = yf.Ticker(f"{symbol}.NS").info
    current_price = info["currentPrice"]
    previous_close = info["regularMarketPreviousClose"]
    diff = current_price - previous_close
    sign = "-"
    indicator = "🔻"
    if diff > 0:
        indicator = "✅"
        sign = "+"
    change_percentage = "{0:.2f}".format((diff / previous_close) * 100).rjust(4)
    diff = "{0:.2f}".format(diff)
    current_price = "{0:.2f}".format(current_price).ljust(10)
    return Messages.getCurrentPriceDetailedMessage(
        symbol=symbol,
        indicator=indicator,
        shortName=info["shortName"],
        current_price=current_price,
        sign=sign,
        diff=diff,
        change_percentage=change_percentage,
    )

def analyzeCandleStickPatterns(symbol: str):
    history = yf.Ticker(f"{symbol}.NS").history(period="1mo")
    RSI = history.ta.rsi() # Relative Strength Index (https://www.rachanaranade.com/blog/rsi)
    class Prediction(Enum):
        POSITIVE = 1
        NEGATIVE = -1
        UNSTABLE = 0
    latest_day = history[-1]
    latest_rsi = RSI[-1]
    prev_day = history[-2]
    predict = dict()

    # Analyze 2 Crows Trend (Reversal of Upward Trend)
    if(latest_day["CDL_2CROWS"] > 0):
        predict["CDL_2CROWS"] = Prediction.NEGATIVE
    else:
        predict["CDL_2CROWS"] = Prediction.UNSTABLE
    
    # Analyze 3 Black Crows Trend (Reversal of Upward Trend)
    if(latest_day["CDL_3BLACKCROWS"] > 0 and RSI[-1] > 60 ):
        predict["CDL_3BLACKCROWS"] = Prediction.NEGATIVE
    else:
        predict["CDL_3BLACKCROWS"] = Prediction.UNSTABLE

    # Analyze 3 Inside Trend ()

#%%
import yfinance as yf
yf.Ticker("MRPL.NS").history(period="1mo").ta.rsi()[-1]
# %%
