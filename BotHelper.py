import telebot
import re
from StockAnalysis import *
import Messages
from CandleStickAnalysis import getFinalSay
from config import ANALYSIS_LIST


def getMonitoringFilebyChatId(chat_id: str):
    return f".\\MonitoringLists\\{chat_id}.txt"


def send_help_message(bot: telebot.TeleBot, message: telebot.types.Message):
    bot.reply_to(message, Messages.getCommandHelperMessage())


def handleAddToList(bot: telebot.TeleBot, message: telebot.types.Message):
    list_item = re.sub(r".*Add\s", "", message.text)
    list_item = list_item.strip()
    path = getMonitoringFilebyChatId(chat_id=message.chat.id)
    try:
        with open(path, "r+") as file:
            for i in file.readlines():
                if list_item in i:
                    bot.reply_to(message, f"{list_item} already exists in the list.")
                    return
    except:
        pass
    if checkSymbolExists(list_item):
        with open(path, "a+") as file:
            file.write(f"{list_item}\n")
            bot.reply_to(message, f"{list_item} has been added")
    else:
        bot.reply_to(message, f"{list_item} is not a valid symbol")


def handleRemoveFromList(bot: telebot.TeleBot, message: telebot.types.Message):
    try:
        with open(getMonitoringFilebyChatId(chat_id=message.chat.id), "r+") as file:
            index = re.sub(r".*Remove\s", "", message.text)
            data = file.readlines()
    except:
        handleFileNotFoundError(bot=bot, message=message)
        return
    flag = 0
    for i in data:
        if index in i:
            data.remove(i)
            flag = 1
    if flag == 0:
        bot.reply_to(message, f"{index} wasn't in the list")
        return
    with open(getMonitoringFilebyChatId(chat_id=message.chat.id), "w+") as file:
        file.writelines(data)
    bot.reply_to(message, f"{index} has been removed")


def handleShowList(bot: telebot.TeleBot, message: telebot.types.Message):
    try:
        with open(getMonitoringFilebyChatId(chat_id=message.chat.id), "r+") as file:
            data = ""
            count = 1
            current_list = file.readlines()
            current_list.sort()
            for i in current_list:
                data += f"{count}. {i}\n"
                count += 1
        bot.reply_to(message, data)
    except:
        handleFileNotFoundError(bot=bot, message=message)


def handleGetCurrentPrice(bot: telebot.TeleBot, message: telebot.types.Message):
    data = "Current Stock Info: \n\n"
    try:
        with open(getMonitoringFilebyChatId(chat_id=message.chat.id), "r") as file:
            symbol_list = file.readlines()
            if len(symbol_list) == 0:
                handleFileNotFoundError(bot=bot, message=message)
                return
            symbol_list.sort()
            for symbol in symbol_list:
                data += getStockDetails(symbol=symbol)
        bot.reply_to(message, data)
    except:
        handleFileNotFoundError(bot=bot, message=message)

def handleGetCurrentPriceSingle(bot: telebot.TeleBot, message: telebot.types.Message, symbol: str):
    if checkSymbolExists(symbol):
        bot.reply_to(message, getStockDetails(symbol=symbol.strip()))
    else:
        bot.reply_to(message, f"{symbol} is not a valid symbol")


def handleFileNotFoundError(bot: telebot.TeleBot, message: telebot.types.Message):
    bot.reply_to(
        message,
        "Could not find anything in your list.\n\nTry adding something to the list or Try again after some time.",
    )

def handleCandle(bot: telebot.TeleBot, message: telebot.types.Message):
    starter_message = "Candle Stick Analysis 📊"
    data = f"{starter_message}: \n\n"
    chat_id = message.chat.id
    try:
        with open(getMonitoringFilebyChatId(chat_id = chat_id), "r") as file:
            symbol_list = file.readlines()
            if len(symbol_list) == 0:
                return
            symbol_list.sort()
            for symbol in symbol_list:
                data += "----------------------------------------------\n\n"
                data += getFinalSay(symbol=symbol.strip())
        if str(chat_id) in ANALYSIS_LIST:
            bot.send_message(chat_id=chat_id, text=data)
        else:
            bot.reply_to(message, text="You are not allowed to use this command")
    except:
        handleFileNotFoundError(bot=bot, message=message)

def handleCandleSingle(bot: telebot.TeleBot, message: telebot.types.Message, symbol: str):
    if checkSymbolExists(symbol):
        chat_id = message.chat.id
        if str(chat_id) in ANALYSIS_LIST:
            data = getFinalSay(symbol=symbol.strip())
            bot.reply_to(message, text=data)
        else:
            bot.reply_to(message, text="You are not allowed to use this command")
    else:
        bot.reply_to(message, f"{symbol} is not a valid symbol")
   