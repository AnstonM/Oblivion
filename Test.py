#%%
import yfinance as yf
import pandas_ta as ta
import numpy as np

history = yf.Ticker("MRPL.NS").history(period="1mo")
isDecreasing = history.ta.decreasing().iloc[-8:-1]
isDecreasing
# weights = [1,2,3,4,5, 6, 7]
# avg = np.average(isDecreasing, weights=weights)
# print(avg)

# %%
import yfinance as yf
import pandas_ta as ta
import numpy as np

history = yf.Ticker("GOLDBEES.NS")
history.info

# %%
