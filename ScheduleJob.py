import os
import telebot
import config


BOT = telebot.TeleBot(config.BOT_TOKEN, threaded=True, num_threads=2)

def candleStickPatterRecognition():
    file_list = os.listdir("./MonitoringLists")
    for i in file_list:
        chat_id = i.removesuffix(".txt")
        print(chat_id)
        BOT.send_message(chat_id=int(chat_id), text="Hi")

candleStickPatterRecognition()