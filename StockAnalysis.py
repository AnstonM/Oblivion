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
        yf.Ticker(f"{symbol}.NS").info["symbol"]
    except: 
        return False
    return True

def getStockDetails(symbol: str):
    try: 
        symbol = symbol.strip()
        info = yf.Ticker(f"{symbol}.NS").info
        current_price = info["currentPrice"]
        previous_close = info["regularMarketPreviousClose"]
        diff = current_price - previous_close
        sign = ""
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
    except:
        return ""
