from config import TOKEN,IDCHAT,URL
import sys
import re
import telebot 
import requests
from bs4 import BeautifulSoup


bot = telebot.TeleBot(TOKEN, parse_mode=None)


sys.path.append("./censure")
from censure import Censor
censor_ru = Censor.get(lang="ru")


# Вывод id сообщения
@bot.message_handler(commands=['id'])
def send_welcome(message):
	bot.reply_to(message, f"Ваше сообщение под № {message.message_id - 1}")


# Вывод id чата
@bot.message_handler(commands=['idc'])
def send_welcome(message):
	bot.reply_to(message, message.chat.id)

# Вывод расписание ИС-24-3
@bot.message_handler(commands=['sc'])
def schedule(message):
    response = requests.get(URL)
    html = response.content
    soup = BeautifulSoup(html, "lxml")
    wp_block_table = soup.find("div",class_="entry-content").find_all("td")

    # Обнуляет файл
    with open('wp_block_table.txt','w', encoding="utf-8") as file_add:
        file_add.write(" ")

    # Записывает расписание с html тегами
    with open('wp_block_table.txt','a', encoding="utf-8") as file_write:
        file_write.write(str(wp_block_table))
    
    # Выводит и обрабатывает текст
    with open('wp_block_table.txt','r', encoding="utf-8") as file_read:
        new_text = file_read.read().replace("[", "").replace("<td>", "").replace("</td>", "").replace(",", "").replace("]", "").replace("преподаватель", "").replace("преподаватель", "")
        clean_text = ' '.join(new_text.split())
        words_time = ["8:00", "9:40", "11:20","13:20","13:00"]
        words_day = ["понедельник", "вторник", "среда", "четверг", "пятница","суббота","ИС-24-3"]
        pattern = r"(" + "|".join(words_time) + r")"
        new_text = re.sub(pattern, r"\n\1", clean_text)
        pattern_day = r"(" + "|".join(words_day) + r")"
        new_text_day = re.sub(pattern_day, r"\n\n\1", new_text)
        bot.reply_to(message,new_text_day)


# Удаляет маты в тексте
@bot.message_handler(content_types=['text'])
def delet_banword(message):
    if message.chat.id != IDCHAT:
        def check_for_profanity(text):
            line_info = censor_ru.clean_line(text)
            _word = line_info[3][0] if line_info[1] else line_info[4][0] if line_info[2] else None
            return not _word is None, _word,line_info

        check_result = check_for_profanity(message.text.lower())

        if check_result[0]:
            print(f"'{message.text}' написал это {message.chat.username}")
            bot.delete_message(message.chat.id, message.message_id)
    else:
        pass


# Удаляет стикету
@bot.message_handler(content_types=["sticker"])
def delet_all_sticer(message):
    if message.chat.id != IDCHAT:
        print(f"стикер отправил {message.chat.username}")
        bot.delete_message(message.chat.id, message.message_id)
    else:
        pass


bot.polling(none_stop=True)