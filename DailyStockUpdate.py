import os
import telebot
import config
from argparse import ArgumentParser
from enum import Enum
from StockAnalysis import getStockDetails
from BotHelper import getMonitoringFilebyChatId, handleFileNotFoundError

class UpdateTime(Enum):
    START = "START"
    MID = "MID"
    END = "END"

def handleGetCurrentPrice(bot: telebot.TeleBot, chat_id: int, starter_message: str):
    data = f"{starter_message}: \n\n"
    try:
        with open(getMonitoringFilebyChatId(chat_id = chat_id), "r") as file:
            symbol_list = file.readlines()
            if len(symbol_list) == 0:
                return
            symbol_list.sort()
            for symbol in symbol_list:
                data += getStockDetails(symbol=symbol)      
        bot.send_message(chat_id=chat_id, text=data)
    except:
        None

BOT = telebot.TeleBot(config.BOT_TOKEN, threaded=True, num_threads=2)


def parse_args():
    parser = ArgumentParser(
        prog="Get Daily Stock Update to Telegram Bot",
    )
    parser.add_argument(
        "-u",
        "--update-time",
        required=False,
        help="Update Time - START, MID or END",
        type=str,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(args)
    starter_message = "MARKET MORNING BELL 🔔"
    if args.update_time == UpdateTime.MID.name:
        starter_message = "MID-DAY MARKET UPDATE 📈"
    elif args.update_time == UpdateTime.END.name:
        starter_message = "MARKET CLOSING UPDATE 🔒"
    file_list = os.listdir("./MonitoringLists")
    for i in file_list:
        chat_id = i.removesuffix(".txt")
        handleGetCurrentPrice(bot=BOT, chat_id=chat_id, starter_message=starter_message)


if __name__ == "__main__":
    main()