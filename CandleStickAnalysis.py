import yfinance as yf
import pandas as pd
import pandas_ta as ta
from enum import Enum
import numpy as np
from config import CANDLE_STICK_PATTERN_LIST


RSI_NEGATIVE_THRESHOLD = 60
RSI_POSITIVE_THRESHOLD = 50


class Prediction(Enum):
    POSITIVE_CONFIRM = 2
    POSITIVE = 1
    NON_DETERMINISTIC = None
    MARKET_INDECISION = 0
    NEGATIVE = -1
    NEGATIVE_CONFIRM = -2


class CandleStickPreliminaryData:
    symbol: str
    pattern_recognition: str | list
    ticker: yf.Ticker  # Yahoo Finance Ticker for getting data
    history: pd.DataFrame  # Historical data for the symbol
    confirmation_parameter: (
        pd.Series
    )  # Parameter to confirm a negative or positive prediction, currently using RSI, Relative Strength Index (https://www.rachanaranade.com/blog/rsi)
    candle_stick_analysis: (
        pd.Series
    )  # Candle Stick Pattern Recognition data from TA-lib using pandas_ta
    # Data for the last trading day
    latest_day_candlestick: pd.Series
    latest_day_history: pd.Series
    latest_confirmation_parameter: float
    # Data on T-1 day
    prev_day: pd.Series
    prev_day_history: pd.Series
    prev_confirmation_parameter: float
    # Determine the trend until today
    wasDownwardTrend: bool
    wasUpwardTrend: bool
    # Maintain the results for all candlestick patterns
    predict: dict
    stop_loss: dict

    def determineWasDownwardTrend(self, offset=1):
        start = (offset * -1) - 6
        end = offset * -1
        isDecreasing = self.history.ta.decreasing().iloc[start:end].tolist()
        weights = [1, 2, 3, 4, 5, 6]
        avg = np.average(isDecreasing, weights=weights)
        return avg > 0.5

    def confirmNegative(self):
        return self.latest_confirmation_parameter > RSI_NEGATIVE_THRESHOLD

    def confirmPositive(self):
        return self.latest_confirmation_parameter < RSI_POSITIVE_THRESHOLD

    def __init__(self, symbol, pattern_recognition: str | list):
        self.symbol = symbol
        self.pattern_recognition = pattern_recognition
        # print("Symbol and Pattern Recognition Setting Initialized...\n")
        self.ticker = yf.Ticker(f"{symbol}.NS")
        self.history = self.ticker.history(period="1mo")
        # print(f"History For {self.symbol} Initialized...\n")
        self.confirmation_parameter = (
            self.history.ta.rsi()
        )  # Relative Strength Index (https://www.rachanaranade.com/blog/rsi)
        self.candle_stick_analysis = self.history.ta.cdl_pattern(
            name=pattern_recognition
        )
        # print("Candle Stick Analysis by TA-lib complete...\n")
        self.latest_day_candlestick = self.candle_stick_analysis.iloc[-1]
        self.latest_day_history = self.history.iloc[-1]
        self.latest_confirmation_parameter = self.confirmation_parameter.iloc[-1]
        # print("Data for last trading day retrieved...\n")
        self.prev_day = self.candle_stick_analysis.iloc[-2]
        self.prev_day_history = self.history.iloc[-2]
        self.prev_confirmation_parameter = self.confirmation_parameter.iloc[-2]
        # print("Data for T-1 trading day retireved...\n")
        self.wasDownwardTrend = self.determineWasDownwardTrend()
        self.wasUpwardTrend = not self.wasDownwardTrend
        self.predict = dict()
        self.stop_loss = dict()
        # print("Preliminary Class Creation Complete...\n\n")

    def ANALYZE_POSITIVE_AND_NEGATIVE(
        self,
        pattern: str,
        trend_check: bool = True,
        was_upward_trend=None,
        was_downward_trend=None,
    ):
        if was_upward_trend == None:
            was_upward_trend = self.wasUpwardTrend
        if was_downward_trend == None:
            was_downward_trend = self.wasDownwardTrend
        try:
            if self.latest_day_candlestick[pattern] > 0 and (
                not trend_check or was_downward_trend
            ):
                if self.latest_confirmation_parameter < RSI_POSITIVE_THRESHOLD:
                    self.predict[pattern] = Prediction.POSITIVE_CONFIRM
                else:
                    self.predict[pattern] = Prediction.POSITIVE
            elif self.latest_day_candlestick[pattern] < 0 and (
                not trend_check or was_upward_trend
            ):
                if self.latest_confirmation_parameter > RSI_NEGATIVE_THRESHOLD:
                    self.predict[pattern] = Prediction.NEGATIVE_CONFIRM
                else:
                    self.predict[pattern] = Prediction.NEGATIVE
            else:
                self.predict[pattern] = Prediction.NON_DETERMINISTIC
        except:
            self.predict[pattern] = None

    def ANALYZE_POSITIVE(
        self,
        pattern: str,
        trend_check: bool = True,
        was_downward_trend=None,
    ):
        if was_downward_trend == None:
            was_downward_trend = self.wasDownwardTrend
        try:
            if self.latest_day_candlestick[pattern] > 0 and (
                not trend_check or was_downward_trend
            ):
                if self.latest_confirmation_parameter < RSI_POSITIVE_THRESHOLD:
                    self.predict[pattern] = Prediction.POSITIVE_CONFIRM
                else:
                    self.predict[pattern] = Prediction.POSITIVE
            else:
                self.predict[pattern] = Prediction.NON_DETERMINISTIC
        except:
            self.predict[pattern] = None

    def ANALYZE_NEGATIVE(
        self, pattern: str, trend_check: bool = True, was_upward_trend=None
    ):
        if was_upward_trend == None:
            was_upward_trend = self.wasUpwardTrend
        try:
            if self.latest_day_candlestick[pattern] < 0 and (
                not trend_check or was_upward_trend
            ):
                if self.latest_confirmation_parameter > RSI_NEGATIVE_THRESHOLD:
                    self.predict[pattern] = Prediction.NEGATIVE_CONFIRM
                else:
                    self.predict[pattern] = Prediction.NEGATIVE
            else:
                self.predict[pattern] = Prediction.NON_DETERMINISTIC
        except:
            self.predict[pattern] = None

    def ANALYZE_MARKET_INDECISION(self, pattern: str):
        try:
            if self.latest_day_candlestick[pattern] != 0:
                self.predict[pattern] = Prediction.MARKET_INDECISION
            else:
                self.predict[pattern] = Prediction.NON_DETERMINISTIC
        except:
            self.predict[pattern] = None


# Analyze 2 Crows Trend (Predict Downward)
def analyze_2Crows(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that two crows is significant when it appears in an uptrend, while this function
    ## does not consider the trend
    preliminary_data.ANALYZE_NEGATIVE(
        pattern="CDL_2CROWS",
        trend_check=True,
        was_upward_trend=not preliminary_data.determineWasDownwardTrend(offset=2),
    )


# Analyze 3 Black Crows Trend (Reversal of Upward Trend)
def analyze_3BlackCrows(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that 3 black crows is significant when it appears after a mature advance or at high levels,
    ## while this function does not consider it
    preliminary_data.ANALYZE_NEGATIVE(
        pattern="CDL_3BLACKCROWS",
        trend_check=True,
        was_upward_trend=not preliminary_data.determineWasDownwardTrend(offset=3),
    )


# Analyze 3 Inside Trend (Trend Reversal)
def analyze_3Inside(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that a three inside up is significant when it appears in a downtrend and a three inside
    ## down is significant when it appears in an uptrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_3INSIDE",
        trend_check=True,
        was_downward_trend=preliminary_data.determineWasDownwardTrend(offset=2),
        was_upward_trend=not preliminary_data.determineWasDownwardTrend(offset=2),
    )


# Analyze 3 Line Strike Trend (Trend Reversal)
def analyze_3LineStrike(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that 3-line strike is significant when it appears in a trend in the same direction of
    ## the first three candles, while this function does not consider it
    last_3_are_downward = (
        np.sum(preliminary_data.history.ta.decreasing().iloc[-4:-1].tolist()) == 3
    )
    last_3_are_upaward = (
        np.sum(preliminary_data.history.ta.decreasing().iloc[-4:-1].tolist()) == 0
    )
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_3LINESTRIKE",
        trend_check=True,
        was_downward_trend=last_3_are_downward,
        was_upward_trend=last_3_are_upaward,
    )


# Analyze 3 Outside Trend (Trend Reversal)
def analyze_3Outside(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    # the user should consider that a three outside up must appear in a downtrend and three outside down must appear
    # in an uptrend, while this function does not consider it
    cdl_3outside_was_downward_trend = preliminary_data.determineWasDownwardTrend(
        offset=2
    )
    cdl_3outside_was_upward_trend = not cdl_3outside_was_downward_trend
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_3OUTSIDE",
        trend_check=True,
        was_downward_trend=cdl_3outside_was_downward_trend,
        was_upward_trend=cdl_3outside_was_upward_trend,
    )


# Analyze 3 Stars In South Trend (Trend Reversal)
def analyze_3StarsInSouth(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that 3 stars in the south is significant when it appears in downtrend, while this function does not consider it.
    initialy_was_downward_trend = preliminary_data.determineWasDownwardTrend(offset=3)
    preliminary_data.ANALYZE_POSITIVE(
        pattern="CDL_3STARSINSOUTH",
        trend_check=True,
        was_downward_trend=initialy_was_downward_trend,
    )


# Analyze 3 White Soldiers Trend (Trend Reversal)
def analyze_3WhiteSoldiers(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that 3 stars in the south is significant when it appears in downtrend, while this function does not consider it.
    initialy_was_downward_trend = preliminary_data.determineWasDownwardTrend(offset=3)
    preliminary_data.ANALYZE_POSITIVE(
        pattern="CDL_3WHITESOLDIERS",
        trend_check=True,
        was_downward_trend=initialy_was_downward_trend,
    )


# Analyze Abandoned Baby Trend (Trend Reversal)
def analyze_AbandonedBaby(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that an abandoned baby is significant when it appears in
    ## an uptrend or downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_ABANDONEDBABY", trend_check=True
    )


# Analyze Advance Block Trend (Predict Downward)
def analyze_AdvanceBlock(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that advance block is significant when it appears in uptrend, while this function does not consider it
    preliminary_data.ANALYZE_NEGATIVE(
        pattern="CDL_ADVANCEBLOCK",
        trend_check=True,
    )


# Analyze Belt Hold Trend (Trend Reversal)
def analyze_BeltHold(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_BELTHOLD", trend_check=False
    )


# Analyze Breakaway Trend (Trend Reversal)
def analyze_BreakAway(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that breakaway is significant in a trend opposite to the last candle, while this function does not consider it
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_BREAKAWAY",
        trend_check=True,
    )


# Analyze Closing Marubozu Trend (Trend Reversal)
def analyze_ClosingMarubozu(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_CLOSINGMARUBOZU", trend_check=False
    )


# Analyze Concealing Baby Swallow Trend (Predict Upward)
def analyze_ConcealingBabySwallow(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that concealing baby swallow is significant when it appears in downtrend, while this function does not consider it
    preliminary_data.ANALYZE_POSITIVE(
        pattern="CDL_CONCEALBABYSWALL",
        trend_check=True,
    )


# Analyze Counter Attack Trend (Trend Reversal)
def analyze_CounterAttack(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_COUNTERATTACK", trend_check=False
    )


# Analyze Dark Cloud Cover Trend (Predict Downward)
def analyze_DarkCloudCover(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that a dark cloud cover is significant when it appears in an uptrend, while this function does not consider it
    preliminary_data.ANALYZE_NEGATIVE(
        pattern="CDL_DARKCLOUDCOVER",
        trend_check=True,
    )


# Analyze Doji Trend (Market Indecision)
def analyze_Doji(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_MARKET_INDECISION(pattern="CDL_DOJI_10_0.1")


# Analyze Doji Star Trend (Trend Reversal)
def analyze_DojiStar(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ##  the user should consider that a doji star is bullish when it appears
    ## in an uptrend and it's bearish when it appears in a downtrend, so to determine the bullishness or
    ## bearishness of the pattern the trend must be analyzed
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_DOJISTAR", trend_check=True
    )


# Analyze Dragonfly Doji Trend (Trend Reversal):
def analyze_DragonflyDoji(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## outInteger is always positive (1 to 100) but this does not mean it is bullish: dragonfly doji must be considered relatively to the trend
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_DRAGONFLYDOJI", trend_check=True
    )


# Analyze Engulfing Trend (Trend Reversal)
def analyze_Engulfing(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## The user should consider that an engulfing must appear in a downtrend if bullish or in an uptrend if bearish, while this function does not consider it
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_ENGULFING", trend_check=True
    )


# Analyze Evening Doji Star Trend (Predict Downward)
def analyze_EveningDojiStar(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that an evening doji star is significant when it appears in an uptrend, while this function does not consider the trend
    preliminary_data.ANALYZE_NEGATIVE(pattern="CDL_EVENINGDOJISTAR", trend_check=True)


# Analyze Evening Star Trend (Predict Downward)
def analyze_EveningStar(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that an evening star is significant when it appears in an uptrend, while this function does not consider the trend
    preliminary_data.ANALYZE_NEGATIVE(pattern="CDL_EVENINGSTAR", trend_check=True)


# Analyze Gap Side by Side White Trend (Trend Reversal)
def analyze_GapSideSideWhite(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TALIB:
    ## the user should consider that upside or downside gap side-by-side white lines is significant when it appears in a trend, while this function does not consider the trend
    was_initially_downward = preliminary_data.determineWasDownwardTrend(offset=3)
    was_initially_upward = not was_initially_downward
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_GAPSIDESIDEWHITE",
        trend_check=True,
        was_downward_trend=was_initially_downward,
        was_upward_trend=was_initially_upward,
    )


# Analyze Grave Stone Doji Trend (Trend Reversal)
def analyze_GraveStoneDoji(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ## outInteger is always positive (1 to 100) but this does not mean it is bullish: gravestone doji must be considered relatively to the trend
    try:
        if preliminary_data.latest_day_candlestick["CDL_GRAVESTONEDOJI"] > 0:
            if preliminary_data.wasDownwardTrend:
                if (
                    preliminary_data.latest_confirmation_parameter
                    < RSI_POSITIVE_THRESHOLD
                ):
                    preliminary_data.predict["CDL_GRAVESTONEDOJI"] = (
                        Prediction.POSITIVE_CONFIRM
                    )
                else:
                    preliminary_data.predict["CDL_GRAVESTONEDOJI"] = Prediction.POSITIVE
            else:
                if (
                    preliminary_data.latest_confirmation_parameter
                    > RSI_NEGATIVE_THRESHOLD
                ):
                    preliminary_data.predict["CDL_GRAVESTONEDOJI"] = (
                        Prediction.NEGATIVE_CONFIRM
                    )
                else:
                    preliminary_data.predict["CDL_GRAVESTONEDOJI"] = Prediction.NEGATIVE
        else:
            preliminary_data.predict["CDL_GRAVESTONEDOJI"] = (
                Prediction.NON_DETERMINISTIC
            )
    except:
        preliminary_data.predict["CDL_GRAVESTONEDOJI"] = None


# Analyze Hammer Trend (Predict Upward)
def analyze_Hammer(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ## the user should consider that a hammer must appear in a downtrend, while this function does not consider it
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_HAMMER", trend_check=True)


# Analyze Hanging Man Trend (Predict Downward)
def analyze_HangingMan(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ## the user should consider that a hanging man must appear in a upward trend, while this function does not consider it
    preliminary_data.ANALYZE_NEGATIVE(pattern="CDL_HANGINGMAN", trend_check=True)


# Analyze Harami Trend (Trend Reversal)
def analyze_Harami(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ## the user should consider that a harami is significant when it appears in a downtrend if bullish or
    ## in an uptrend when bearish, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_HARAMI", trend_check=True
    )


# Analyze Harami Cross Trend (Trend Reversal)
def analyze_HaramiCross(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ## the user should consider that a harami cross is significant when it appears in a downtrend if bullish or
    ## in an uptrend when bearish, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_HARAMICROSS", trend_check=True
    )


# Analyze High Wave Trend (Market Indecision)
def analyze_HighWave(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_MARKET_INDECISION(pattern="CDL_HIGHWAVE")


# Analyze Modified Hikkake Trend (Trend Reversal)
def analyze_ModifiedHikkake(preliminary_data: CandleStickPreliminaryData):
    # Confirmation could come in the next 3 days with:
    #   - a day that closes higher than the high (lower than the low) of the 2nd candle
    # outInteger[confirmationbar] is equal to 100 + the bullish hikkake result or -100 - the bearish hikkake result
    # Note: if confirmation and a new hikkake come at the same bar, only the new hikkake is reported (the new hikkake
    # overwrites the confirmation of the old hikkake)
    # the user should consider that modified hikkake is a reversal pattern, while hikkake could be both a reversal
    # or a continuation pattern, so bullish (bearish) modified hikkake is significant when appearing in a downtrend
    # (uptrend)
    hikkake_seen_before = np.sum(
        preliminary_data.candle_stick_analysis["CDL_HIKKAKEMOD"].iloc[-5:-1].tolist()
    )
    was_initially_downward = preliminary_data.determineWasDownwardTrend(offset=3)
    was_initially_upward = not was_initially_downward
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_HIKKAKEMOD",
        trend_check=True,
        was_downward_trend=hikkake_seen_before > 0 and was_initially_downward,
        was_upward_trend=hikkake_seen_before < 0 and was_initially_upward,
    )


# Analyze Homing Pigeon Trend (Predict Upwards)
def analyze_HomingPigeon(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that homing pigeon is significant when it appears in a downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_HOMINGPIGEON", trend_check=True)


# Analyze Identical 3 Crows (Predict Downward)
def analyze_Identical3Crows(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that identical 3 crows is significant when it appears after a mature advance or at high levels,
    ## while this function does not consider it
    was_initially_upward = not preliminary_data.determineWasDownwardTrend(offset=3)
    preliminary_data.ANALYZE_NEGATIVE(
        pattern="CDL_IDENTICAL3CROWS",
        trend_check=True,
        was_upward_trend=was_initially_upward,
    )


# Analyze In Neck Trend (Predict Downward Continuation)
def analyze_InNeck(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that in neck is significant when it appears in a downtrend, while this function does not consider the trend
    try:
        if (
            preliminary_data.latest_day_candlestick["CDL_INNECK"] < 0
            and preliminary_data.wasDownwardTrend
        ):
            if preliminary_data.latest_confirmation_parameter > RSI_NEGATIVE_THRESHOLD:
                preliminary_data.predict["CDL_INNECK"] = Prediction.NEGATIVE_CONFIRM
            else:
                preliminary_data.predict["CDL_INNECK"] = Prediction.NEGATIVE
        else:
            preliminary_data.predict["CDL_INNECK"] = Prediction.NON_DETERMINISTIC
    except:
        preliminary_data.predict["CDL_INNECK"] = None


# Analyze Inverted Hammer Trend (Predict Upward)
def analyze_InvertedHammer(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that inverted hammer is significant when it appears in a downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_INVERTEDHAMMER", trend_check=True)


# Analyze Kicking Trend (Trend Reversal)
def analyze_Kicking(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_KICKING", trend_check=False
    )


# Analyze Kicking By Length Trend (Trend Reversal)
def analyze_KickingByLength(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_KICKINGBYLENGTH", trend_check=False
    )


# Analyze Ladder Botton Trend (Predict Upward)
def analyze_LadderBottom(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ## the user should consider that ladder bottom is significant when it appears in a downtrend, while this function does not consider it
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_LADDERBOTTOM", trend_check=True)


# Analyze Long Legged Doji Trend (Market Indecision)
def analyze_LongLeggedDoji(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_MARKET_INDECISION(pattern="CDL_LONGLEGGEDDOJI")


# Analyze Long Line Trend (Trend Reversal)
def analyze_LongLine(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_LONGLINE", trend_check=False
    )


# Analyze Marubozu Trend (Trend Setter)
def analyze_Marubozu(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_MARUBOZU", trend_check=False
    )


# Analyze Matching Low Trend (Predict Upward)
def analyze_MatchingLow(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_MATCHINGLOW", trend_check=False)


# Analyze Mat Hold Trend (Predict Upward)
def analyze_MatHold(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_MATHOLD", trend_check=False)


# Analyze Morning Doji Star Trend (Predict Upwards)
def analyze_MorningDojiStar(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that a morning star is significant when it appears in a downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_MORNINGDOJISTAR", trend_check=True)


# Analyze Morning Star Trend (Predict Upwards)
def analyze_MorningStar(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that a morning star is significant when it appears in a downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_MORNINGSTAR", trend_check=True)


# Analyze On Neck Trend (Downward Continuation)
def analyze_OnNeck(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ## the user should consider that on-neck is significant when it appears in a downtrend, while this function does not consider it
    try:
        if (
            preliminary_data.latest_day_candlestick["CDL_ONNECK"] < 0
            and preliminary_data.wasDownwardTrend
        ):
            if preliminary_data.latest_confirmation_parameter > RSI_NEGATIVE_THRESHOLD:
                preliminary_data.predict["CDL_ONNECK"] = Prediction.NEGATIVE_CONFIRM
            else:
                preliminary_data.predict["CDL_ONNECK"] = Prediction.NEGATIVE
        else:
            preliminary_data.predict["CDL_ONNECK"] = Prediction.NON_DETERMINISTIC
    except:
        preliminary_data.predict["CDL_ONNECK"] = None


# Analyze Piercing Trend (Predict Upward)
def analyze_Piercing(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that a piercing is significant when it appears in a downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_PIERCING", trend_check=True)


# Analyze Rickshaw Man (Market Indecision)
def analyze_RickshawMan(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  outInteger is always positive (1 to 100) but this does not mean it is bullish: rickshaw man shows uncertainty
    preliminary_data.ANALYZE_MARKET_INDECISION(pattern="CDL_RICKSHAWMAN")


# Analyze Rise Fall 3 Methods Trend (Trend Continuation)
def analyze_RiseFall3Methods(preliminary_data: CandleStickPreliminaryData):
    try:
        if preliminary_data.latest_day_candlestick["CDL_RISEFALL3METHODS"] > 0:
            if preliminary_data.latest_confirmation_parameter < RSI_POSITIVE_THRESHOLD:
                preliminary_data.predict["CDL_RISEFALL3METHODS"] = (
                    Prediction.POSITIVE_CONFIRM
                )
            else:
                preliminary_data.predict["CDL_RISEFALL3METHODS"] = Prediction.POSITIVE
        elif preliminary_data.latest_day_candlestick["CDL_RISEFALL3METHODS"] < 0:
            if preliminary_data.latest_confirmation_parameter > RSI_NEGATIVE_THRESHOLD:
                preliminary_data.predict["CDL_RISEFALL3METHODS"] = (
                    Prediction.NEGATIVE_CONFIRM
                )
            else:
                preliminary_data.predict["CDL_RISEFALL3METHODS"] = Prediction.NEGATIVE
        else:
            preliminary_data.predict["CDL_RISEFALL3METHODS"] = (
                Prediction.NON_DETERMINISTIC
            )
    except:
        preliminary_data.predict["CDL_RISEFALL3METHODS"] = None


# Analyze Seperating Lines Trend (Trend Continuation)


# Analyze Shooting Star Trend (Predict Downward)
def analyze_ShootingStar(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that a shooting star is significant when it appears in a uptrend, while this function does not consider the trend
    preliminary_data.ANALYZE_NEGATIVE(pattern="CDL_SHOOTINGSTAR", trend_check=True)


# Analyze Short Line Trend (Market Indecision)
def analyze_ShortLine(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_MARKET_INDECISION(pattern="CDL_SHORTLINE")


# Analyze Spinning Top Trend (Market Indecision)
def analyze_SpinningTop(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_MARKET_INDECISION(pattern="CDL_SPINNINGTOP")


# Analyze Stalled Pattern Trend (Predict Downward)
def analyze_StalledPattern(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that a stalled pattern is significant when it appears in a uptrend, while this function does not consider the trend
    preliminary_data.ANALYZE_NEGATIVE(pattern="CDL_STALLEDPATTERN", trend_check=True)


# Analyze Stick Sandwich Trend (Predict Upward)
def analyze_StickSandwich(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that a stick sandwich is significant when it appears in a downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE(
        pattern="CDL_STICKSANDWICH",
        trend_check=True,
        was_downward_trend=preliminary_data.determineWasDownwardTrend(offset=2),
    )


# Analyze Stick Sandwich Trend (Predict Upward)
def analyze_Takuri(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  the user should consider that a takuri is significant when it appears in a downtrend, while this function does not consider the trend
    preliminary_data.ANALYZE_POSITIVE(pattern="CDL_TAKURI", trend_check=True)


# Analyze Tasuki Gap Trend (Trend Reversal)
def analyze_TasukiGap(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_TASUKIGAP",
        trend_check=True,
        was_downward_trend=preliminary_data.determineWasDownwardTrend(offset=2),
        was_upward_trend=not preliminary_data.determineWasDownwardTrend(offset=2),
    )


# Analyze Thrusting Trend (Predict Downward)
def analyze_Thrusting(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_NEGATIVE(pattern="CDL_THRUSTING", trend_check=True)


# Analyze Tri Star Trend (Trend Reversal)
def analyze_TriStar(preliminary_data: CandleStickPreliminaryData):
    preliminary_data.ANALYZE_POSITIVE_AND_NEGATIVE(
        pattern="CDL_TRISTAR",
        trend_check=False,
        was_downward_trend=preliminary_data.determineWasDownwardTrend(offset=2),
        was_upward_trend=not preliminary_data.determineWasDownwardTrend(offset=2),
    )


# Analyze Unique 3 River Trend (Predict Upward)
def analyze_Unique3River(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUNTED BY TA-LIB
    ##  unique 3 river is always bullish and should appear in a downtrend
    preliminary_data.ANALYZE_POSITIVE(
        pattern="CDL_UNIQUE3RIVER",
        trend_check=True,
        was_downward_trend=preliminary_data.determineWasDownwardTrend(offset=2),
    )


# Analyze Upside Gap 2 Crows Trend (predict Downward)
def analyze_UpsideGap2Crows(preliminary_data: CandleStickPreliminaryData):
    # NOT ACCOUTED BY TA-LIB
    ## the user should consider that an upside gap two crows is significant when it appears in an uptrend
    preliminary_data.ANALYZE_NEGATIVE(
        pattern="CDL_UPSIDEGAP2CROWS",
        trend_check=True,
        was_upward_trend=not preliminary_data.determineWasDownwardTrend(offset=2),
    )


# Analyze Upside/Downside Gap 3 Method Trend (Trend Continuation)
def analyze_XsideGap3Method(preliminary_data: CandleStickPreliminaryData):
    try:
        if (
            preliminary_data.latest_day_candlestick["CDL_XSIDEGAP3METHODS"] > 0
            and preliminary_data.wasUpwardTrend
        ):
            if preliminary_data.latest_confirmation_parameter < RSI_POSITIVE_THRESHOLD:
                preliminary_data.predict["CDL_XSIDEGAP3METHODS"] = (
                    Prediction.POSITIVE_CONFIRM
                )
            else:
                preliminary_data.predict["CDL_XSIDEGAP3METHODS"] = Prediction.POSITIVE
        elif (
            preliminary_data.latest_day_candlestick["CDL_XSIDEGAP3METHODS"] < 0
            and preliminary_data.wasDownwardTrend
        ):
            if preliminary_data.latest_confirmation_parameter > RSI_NEGATIVE_THRESHOLD:
                preliminary_data.predict["CDL_XSIDEGAP3METHODS"] = (
                    Prediction.NEGATIVE_CONFIRM
                )
            else:
                preliminary_data.predict["CDL_XSIDEGAP3METHODS"] = Prediction.NEGATIVE
        else:
            preliminary_data.predict["CDL_XSIDEGAP3METHODS"] = (
                Prediction.NON_DETERMINISTIC
            )
    except:
        preliminary_data.predict["CDL_XSIDEGAP3METHODS"] = None


def analyzeCandleStickPatterns(symbol: str):
    preliminary_data = CandleStickPreliminaryData(
        symbol=symbol, pattern_recognition=CANDLE_STICK_PATTERN_LIST
    )
    analyze_2Crows(preliminary_data)
    analyze_3BlackCrows(preliminary_data)
    analyze_3Inside(preliminary_data)
    analyze_3LineStrike(preliminary_data)
    analyze_3Outside(preliminary_data)
    analyze_3StarsInSouth(preliminary_data)
    analyze_3WhiteSoldiers(preliminary_data)
    analyze_AbandonedBaby(preliminary_data)
    analyze_AdvanceBlock(preliminary_data)
    analyze_BeltHold(preliminary_data)
    analyze_BreakAway(preliminary_data)
    analyze_ClosingMarubozu(preliminary_data)
    analyze_ConcealingBabySwallow(preliminary_data)
    analyze_CounterAttack(preliminary_data)
    analyze_DarkCloudCover(preliminary_data)
    analyze_Doji(preliminary_data)
    analyze_DojiStar(preliminary_data)
    analyze_DragonflyDoji(preliminary_data)
    analyze_Engulfing(preliminary_data)
    analyze_EveningDojiStar(preliminary_data)
    analyze_EveningStar(preliminary_data)
    analyze_GapSideSideWhite(preliminary_data)
    analyze_GraveStoneDoji(preliminary_data)
    analyze_Hammer(preliminary_data)
    analyze_HangingMan(preliminary_data)
    analyze_Harami(preliminary_data)
    analyze_HaramiCross(preliminary_data)
    analyze_HighWave(preliminary_data)
    analyze_ModifiedHikkake(preliminary_data)
    analyze_HomingPigeon(preliminary_data)
    analyze_Identical3Crows(preliminary_data)
    analyze_InNeck(preliminary_data)
    analyze_InvertedHammer(preliminary_data)
    analyze_Kicking(preliminary_data)
    analyze_KickingByLength(preliminary_data)
    analyze_LadderBottom(preliminary_data)
    analyze_LongLeggedDoji(preliminary_data)
    analyze_LongLine(preliminary_data)
    analyze_Marubozu(preliminary_data)
    analyze_MatchingLow(preliminary_data)
    analyze_MatHold(preliminary_data)
    analyze_MorningDojiStar(preliminary_data)
    analyze_MorningStar(preliminary_data)
    analyze_OnNeck(preliminary_data)
    analyze_Piercing(preliminary_data)
    analyze_RickshawMan(preliminary_data)
    analyze_RiseFall3Methods(preliminary_data)
    analyze_ShootingStar(preliminary_data)
    analyze_ShortLine(preliminary_data)
    analyze_SpinningTop(preliminary_data)
    analyze_StalledPattern(preliminary_data)
    analyze_StickSandwich(preliminary_data)
    analyze_Takuri(preliminary_data)
    analyze_TasukiGap(preliminary_data)
    analyze_Thrusting(preliminary_data)
    analyze_TriStar(preliminary_data)
    analyze_Unique3River(preliminary_data)
    analyze_UpsideGap2Crows(preliminary_data)
    analyze_XsideGap3Method(preliminary_data)
    return preliminary_data.predict


def getFinalSay(symbol: str):
    ticker = yf.Ticker(f"{symbol}.NS")
    short_name = ticker.info["shortName"]
    data = ""
    positive = ""
    negative = ""
    market_indecision = ""
    predict = analyzeCandleStickPatterns(symbol)
    # pprint(predict)
    data += f"Symbol:\t\t{symbol}\nName:\t\t{short_name}\n\n"
    data += f"Analysis Suggestion:\t\t"
    sum = 0
    indecisive_count = 0
    for k, v in predict.items():
        name = k.removeprefix("CDL_")
        if v.value == 2:
            positive += f"- {name} confirms BUY\n"
        elif v.value == 1:
            positive += f"- {name} suggests BUY\n"
        elif v.value == -2:
            negative += f"- {name} confirms SELL\n"
        elif v.value == -1:
            negative += f"- {name} suggests SELL\n"
        elif v.value == 0:
            market_indecision += f"- {name} suggests INDECISION\n"
            indecisive_count += 1
        if v.value != None:
            sum += v.value
    if indecisive_count > abs(sum):
        data += "INDECISION"
    elif sum > 0:
        data += "BUY"
    elif sum < 0:
        data += "SELL"
    else:
        data += "N/A"
    data += "\n\n"
    if positive != "":
        data += "🟢 Positive Suggestions:\n\n"
        data += positive
        data += "\n\n"
    if negative != "":
        data += "🚩 Negative Suggestions:\n\n"
        data += negative
        data += "\n\n"
    if market_indecision != "":
        data += "🤔 Market Indecision:\n\n"
        data += market_indecision
        data += "\n\n"
    return data
