import os
import telebot
import config
from CandleStickAnalysis import getFinalSay
from BotHelper import getMonitoringFilebyChatId, handleFileNotFoundError
from config import ANALYSIS_LIST



def handleGetCandleStickAnalysis(bot: telebot.TeleBot, chat_id: int, starter_message: str):
    data = f"{starter_message}: \n\n"
    try:
        with open(getMonitoringFilebyChatId(chat_id = chat_id), "r") as file:
            symbol_list = file.readlines()
            if len(symbol_list) == 0:
                return
            symbol_list.sort()
            for symbol in symbol_list:
                data += "----------------------------------------------\n\n"
                data += getFinalSay(symbol=symbol.strip())
        if chat_id in ANALYSIS_LIST:
            print(chat_id)     
            bot.send_message(chat_id=chat_id, text=data)
    except:
        handleFileNotFoundError(bot=bot, chat_id=chat_id)


BOT = telebot.TeleBot(config.BOT_TOKEN, threaded=True, num_threads=2)

def main():
    file_list = os.listdir("./MonitoringLists")
    starter_message = "Candle Stick Analysis 📊"
    for i in file_list:
        chat_id = i.removesuffix(".txt")
        handleGetCandleStickAnalysis(bot=BOT, chat_id=chat_id, starter_message=starter_message)


if __name__ == "__main__":
    main()