import telebot
import config
import BotHelper
import Messages
import re
from StockAnalysis import getStockDetails

BOT = telebot.TeleBot(config.BOT_TOKEN, threaded=True, num_threads=4)
@BOT.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    BOT.reply_to(message, Messages.getCommandHelperMessage(starterMessage="Welcome to Oblivion Bot v0.1"))

@BOT.message_handler(func=lambda msg: msg.text=="Help")
@BOT.message_handler(commands=['Help', 'help'])
def help(message):
    BotHelper.send_help_message(bot=BOT, message=message)

@BOT.message_handler(func=lambda msg: "Add " in msg.text)
def add(message):
    BotHelper.handleAddToList(bot=BOT, message=message)

@BOT.message_handler(func=lambda msg: "Remove " in msg.text)
def delete(message):
    BotHelper.handleRemoveFromList(bot=BOT, message=message)
    

@BOT.message_handler(commands=['ShowList', "showlist", "showList", "Showlist"])
def showeList(message):
    BotHelper.handleShowList(bot=BOT, message=message)
    

@BOT.message_handler(commands=['Current', 'current'])
def currentData(message):
    symbol = re.sub(r".*CURRENT\s*", "", message.text.upper())
    symbol = symbol.strip()
    if symbol == "":
        BotHelper.handleGetCurrentPrice(bot=BOT, message=message)
    else:
        BotHelper.handleGetCurrentPriceSingle(bot=BOT, message=message, symbol=symbol)


@BOT.message_handler(commands=["Candle", "candle"])
def candle(message):
    symbol = re.sub(r".*CANDLE\s*", "", message.text.upper())
    symbol = symbol.strip()
    if symbol == "":
        BotHelper.handleCandle(bot=BOT, message=message)
    else:
        BotHelper.handleCandleSingle(bot=BOT, message=message, symbol=symbol)

BOT.infinity_polling(long_polling_timeout=None, timeout=None)
